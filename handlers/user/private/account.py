from aiogram import types, Dispatcher, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from fsm.user.private import UpdateProfileFSM

from markups.user.account import account_manage_markup, update_profile_markup

from database.dao import UserDAO
from database.utils import connection

from text import get_account_description


@connection
async def send_account_info(c: types.CallbackQuery, db_session: AsyncSession):
    await c.answer()

    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)

    await c.message.answer(
        text=get_account_description(
            rating=user.profile.rating,
            user_name=user.profile.name,
            alias=user.profile.alias,
            reg_date=user.register_date,
            interests=user.profile.interests,
            city=user.profile.city
        ),
        reply_markup=account_manage_markup
    )


async def ask_what_to_change(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(UpdateProfileFSM.key_state)
    await c.message.answer(
        "Выберите, что хотите поменять",
        reply_markup=update_profile_markup
    )

    await c.answer()


async def ask_value(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(UpdateProfileFSM.value_state)
    key = c.data.split('_')[1]
    await state.update_data(key=key)

    message_detail = {
        "name": "новое имя",
        "alias": "новый псевдоним",
        "interests": "список интересов"
    }

    await c.message.answer(f"Введите {message_detail.get(key, 'новое значение')}")
    await c.answer()


@connection
async def update_value(m: types.Message, state: FSMContext, db_session: AsyncSession):
    s_data = await state.get_data()

    user = await UserDAO.get_obj(db_session, telegram_id=m.from_user.id)
    user.__setattr__(s_data["key"], m.text.strip())
    await db_session.commit()


    await m.answer(
        text="Ваш обновленный профиль:\n\n" + get_account_description(
            rating=user.profile.rating,
            user_name=user.profile.name,
            alias=user.profile.alias,
            reg_date=user.register_date,
            interests=user.profile.interests,
            city=user.profile.city
        ),
        reply_markup=account_manage_markup
    )


def register_account_handlers(dp: Dispatcher):
    dp.callback_query.register(send_account_info, F.data == "lk")
    dp.callback_query.register(ask_what_to_change, F.data == "update_profile")
    dp.callback_query.register(ask_value, F.data.startswith("change_"), StateFilter(UpdateProfileFSM.key_state))
    dp.message.register(update_value, StateFilter(UpdateProfileFSM.value_state))
