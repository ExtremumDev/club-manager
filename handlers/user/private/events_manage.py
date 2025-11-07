from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter


from sqlalchemy import delete


from filters.user_filters import AdminFilter

from database.utils import connection
from database.dao import MembersEventDAO, EventMembershipDAO

from markups.admin.event_manage import get_event_type_markup

from utils.paging.user_events_paging import UserEventsPaging

from utils.enums import EventType


async def ask_event_type(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer(
        "Выберите какие события хотите посмотреть",
        reply_markup=get_event_type_markup("mye")
    )


@connection
async def send_event_list(c: types.CallbackQuery, db_session, *args):
    event_type = c.data.split('_')[1]
    
    paging = UserEventsPaging(EventType(int(event_type)))
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
async def send_event_info(c: types.CallbackQuery, db_session, *args):
    event_id = c.data.split('_')[1]

    event = await MembersEventDAO.get_obj(db_session, id=int(event_id))

    if event:
        message_text = event.event_type.get_card_text(**event.model_to_dict())

        await c.message.answer(
            text=message_text
        )
        await c.answer()
    else:
        await c.answer("Событие не найдено", show_alert=True)


def register_events_manage_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_event_type, F.data == "my_events")
    dp.callback_query.register(send_event_list, F.data.startswith("myeeventtype_"))
    UserEventsPaging.register_paging_handlers(dp)
    dp.callback_query.register(send_event_info, F.data.startswith("ueventm_"))
