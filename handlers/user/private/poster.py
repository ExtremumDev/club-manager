from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from markups.admin.event_manage import get_event_type_markup
from markups.user.events import get_take_part_in_event_markup, take_part_in_week_events_markup

from database.dao import MembersEventDAO, EventMembershipDAO, UserDAO
from database.utils import connection

from utils.enums import EventType
from utils.paging.user_events_paging import EventsPaging


async def ask_event_type(c: types.CallbackQuery):
    await c.message.answer(
        "Выберите, какие мероприятия хотите посмотреть",
        reply_markup=get_event_type_markup("af")
    )
    await c.answer()


@connection
async def send_event_list(c: types.CallbackQuery, db_session: AsyncSession, *args):
    event_type = c.data.split('_')[1]

    paging = EventsPaging(EventType(int(event_type)), prefix="af")
    await paging.get_queryset(
        db_session
    )
    await paging.get_current_page()

    await c.message.answer(
        "Выберите мероприятие, которое хотите посмотреть",
        reply_markup=paging.get_reply_markup()
    )
    await c.answer()


@connection
async def send_event_info(c: types.CallbackQuery, db_session: AsyncSession, *args):
    event_id = c.data.split('_')[1]

    event = await MembersEventDAO.get_obj(db_session, id=int(event_id))

    if event:
        message_text = event.event_type.get_card_text(**event.model_to_dict())

        await c.message.answer(
            text=message_text,
            reply_markup=get_take_part_in_event_markup(int(event_id), event.event_type)
        )
        await c.answer()
    else:
        await c.answer("Событие не найдено", show_alert=True)


@connection
async def send_events_for_week(c: types.CallbackQuery, db_session: AsyncSession, *args):
    events = await MembersEventDAO.get_this_week_events(db_session)

    if events:
        message_text = ""
        events_id = []
        events_markup = []

        for e in events:
            message_text += e.event_type.get_card_text(**e.model_to_dict())
            message_text += "\n"

            events_id.append(str(e.id))

            events_markup.append(
                [
                    types.InlineKeyboardButton(
                        text="Записаться на " + e.event_type.get_event_name(),
                        callback_data=f"takepevent_{e.id}_{e.event_type}"
                    )
                ]
            )

        parts = []

        for i in range(0, len(message_text), 4096):
            parts.append(message_text[i: i + 4096])

        last_message = None
        for p in parts:
            last_message = await c.message.answer(
                p
            )
        markup = take_part_in_week_events_markup('_'.join(events_id))

        markup.inline_keyboard.extend(events_markup)
        await last_message.edit_reply_markup(
            reply_markup=markup
        )
        await c.answer()
    else:

        await c.answer("Не найдено событий на эту неделю", show_alert=True)


@connection
async def take_part_in_week_events(c: types.CallbackQuery, db_session: AsyncSession, *args):
    events_id = list(map(lambda n: int(n), c.data.split('_')[1:]))

    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)

    events = await MembersEventDAO.get_events_from_list(db_session, events_id)

    failed_events = []

    for event in events:
        user_membership = await EventMembershipDAO.get_obj(
            db_session,
            user_id=user.id,
            event_id=event.id
        )

        if not user_membership:
            if event.members_left > 0:
                event.members_left -= 1

                await EventMembershipDAO.add(
                    db_session,
                    user_id=user.id,
                    event_id=event.id,
                    is_member=True
                )
            else:
                failed_events.append(event)

    message_text = ""

    if failed_events:
        message_text += "Не удалось записать вас на следующие события:"
        for f_e in failed_events:
            message_text += f_e.event_type.get_event_name()

        message_text += " - недостаточно мест\n\n"

        message_text += "На остальные события вы успешно записаны!"

    else:
        message_text = "Вы успешно записаны на все события!"

    await c.message.answer(
        message_text
    )

    await db_session.commit()



def register_poster_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_event_type, F.data == "poster")
    dp.callback_query.register(send_event_list, F.data.startswith("afeventtype_"))
    EventsPaging.register_paging_handlers(dp, data_prefix="af")
    dp.callback_query.register(send_event_info, F.data.startswith("afeventm_"))

    dp.callback_query.register(send_events_for_week, F.data == "weeks_events")
    dp.callback_query.register(take_part_in_week_events, F.data.startswith("manytakep_"))

