from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter


from sqlalchemy import delete


from filters.user_filters import AdminFilter

from database.utils import connection
from database.dao import MembersEventDAO, EventMembershipDAO

from markups.admin.event_manage import get_event_type_markup

from utils.paging.events_paging import EventsPaging


async def ask_event_type(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer(
        "Выберите какие события хотите посмотреть",
        reply_markup=get_event_type_markup("mye")
    )


async def send_even


def register_events_manage_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_event_type, F.data == "my_events")
