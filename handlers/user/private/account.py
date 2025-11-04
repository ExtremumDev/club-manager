from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from markups.user.main import account_manage_markup

from database.dao import UserDAO
from database.utils import connection

from text import get_account_description


@connection
async def send_account_info(c: types.CallbackQuery, db_session: AsyncSession):
    await c.answer()

    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)

    await c.message.answer(
        text=get_account_description(user.rating),
        reply_markup=account_manage_markup
    )


def register_account_handlers(dp: Dispatcher):
    dp.callback_query.register(send_account_info, F.data == "lk")
