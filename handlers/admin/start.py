from aiogram.filters import CommandStart, StateFilter
from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType

from database.dao import UserDAO
from database.utils import connection

from filters.user_filters import AdminFilter
from markups.admin.main import main_admin_markup, main_markup_for_admin


@connection
async def start_cmd(m: types.Message, state: FSMContext, db_session, *args):
    await state.clear()

    user = await UserDAO.get_obj(
        db_session,
        telegram_id=m.from_user.id,
    )
    if not user:
        await UserDAO.register_user(
            db_session,
            telegram_id=m.from_user.id,
            username=m.from_user.username,
            has_bot_chat=True,
            is_admin=True
        )

    await m.answer(
        text="Добро пожаловать!",
        reply_markup=main_markup_for_admin
    )


async def open_admin_panel(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer(
        "Открыта панель администратора",
        reply_markup=main_admin_markup
    )


async def back_to_menu(c: types.CallbackQuery):
    await c.answer()
    await c.message.answer(
        "Открыто главное меню",
        reply_markup=main_markup_for_admin
    )


def register_start_handlers(dp: Dispatcher) -> None:
    dp.message.register(
        start_cmd,
        CommandStart(),
        AdminFilter(),
        F.chat.type == ChatType.PRIVATE,
        StateFilter('*')
    )
    dp.callback_query.register(
        open_admin_panel,
        F.data == "admin_panel",
        AdminFilter()
    )
    dp.callback_query.register(
        back_to_menu,
        F.data == "back_to_menu",
        AdminFilter()
    )

