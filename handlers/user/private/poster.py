from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from markups.admin.event_manage import get_event_type_markup
from markups.user.events import get_take_part_in_event_markup

from database.dao import MembersEventDAO
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

    paging = EventsPaging(EventType(int(event_type)))
    await paging.get_queryset(
        db_session,
        c.from_user.id
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


def register_poster_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_event_type, F.data == "poster")
    dp.callback_query.register(send_event_list, F.data.startswith("afeeventtype_"))
    EventsPaging.register_paging_handlers(dp, data_prefix="af")
    dp.callback_query.register(send_event_info, F.data.startswith("afventm_"))

