from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter


from sqlalchemy import delete


from filters.user_filters import AdminFilter

from database.utils import connection
from database.dao import MembersEventDAO, EventMembershipDAO

from markups.admin.event_manage import get_event_type_markup, get_event_manage_markup

from utils.paging.events_paging import EventsPaging

from fsm.admin.events_manage import NewEventMemberFSM

from utils.enums import EventType


async def ask_event_type(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer(
        text="Выберите события, которые хотите просмотреть",
        reply_markup=get_event_type_markup("em")
    )


@connection
async def send_event_list(c: types.CallbackQuery, db_session, *args):
    event_type = c.data.split('_')[1]
    
    paging = EventsPaging()

    await paging.get_queryset(db_session, event_type=EventType(int(event_type)))
    await paging.get_current_page()

    await c.message.answer(
        "Выберите событие",
        reply_markup=paging.get_reply_markup(extra_data=f"_{event_type}")
    )

    await c.answer()


@connection
async def send_event_info(c: types.CallbackQuery, db_session, *args):
    event_id = c.data.split('_')[1]

    event = await MembersEventDAO.get_event_with_members(db_session, int(event_id))

    if event:
        message_text = event.event_type.get_card_text(**event.model_to_dict())

        if event.members:
            i = 1
            for member in evet.members:
                if member.is_member:
                    if member.is_bot_user:
                        message_text += f"\n{i}) @{member.user.username}"
                    else:
                        message_text += f"\n{i}) {member.name}"
        else:
            message_text += "\n\n К данному мероприятию пока никто не присоединился"


        await c.message.answer(
            text=message_text,
            reply_markup=get_event_manage_markup(
                event_id
            )
        )
        await c.answer()
    else:
        await c.answer("Событие не найдено", show_alert=True)
            

@connection
async def ask_member_name(c: types.CallbackQuery, state: FSMContext, db_session, *args):
    event_id = c.data.split('_')

    event = await MembersEventDAO.get_obj(db_session, id=event_id)

    if event:
        if event.members_left > 0:
            await state.set_state(
                NewEventMemberFSM.member_name_state
            )

            await state.update_data(
                event_id=event_id
            )
            await c.message.answer(
                "Введите имя участника"
            )
            await c.answer()
        else:
            await c.answer("На мероприятии не осталось свободных мест", show_alert=True)
    else:
        await c.answer("Событие не найдено", show_alert=True)


@connection
async def add_new_member(m: types.Message, state: FSMContext, db_session, *args):
    s_data = await state.get_data()
    event_id = s_data['event_id']
    await state.clear()

    await EventMembershipDAO.add(
        db_session,
        event_id=event_id,
        is_bot_user=False,
        name=m.text
    )

    event = await MembersEventDAO.get_obj(db_session, id=event_id)
    event.members_left -= 1
    await db_session.commit()

    await m.answer(
        "Участник успешно добавлен!"
    )

@connection
async def delete_event(c: types.CallbackQuery, db_session, *args):
    event_id = c.data.split('_')[1]

    event = await MembersEventDAO.get_obj(db_session, id=event_id)

    if event:
        await db_session.delete(event)
        await db_session.commit()

        await c.answer(
            "Событие успешно удалено",
            show_alert=True
        )
    else:
        await c.answer(
            "Событие не найдеено!",
            show_alert=True
        )


def register_event_manage_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_event_type, AdminFilter(), F.data == "manage_events")
    dp.callback_query.register(send_event_list, F.data.startswith("emeventtype_"))
    EventsPaging.register_paging_handlers(dp)
    dp.callback_query.register(send_event_info, F.data.startswith("eventm_"))
    dp.callback_query.register(ask_member_name, F.data.startswith("addmember_"))
    dp.message.register(add_new_member, StateFilter(NewEventMemberFSM.member_name_state))
    dp.callback_query.register(delete_event, F.data.startswith("deleteevent_"))
