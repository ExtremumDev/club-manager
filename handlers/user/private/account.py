from aiogram import types, Dispatcher, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from fsm.user.private import UpdateProfileFSM

from markups.user.account import account_manage_markup, update_profile_markup
from markups.user.dating import dating_fun_rate_markup

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
            reg_date=user.register_date,
            interests=user.profile.interests,
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
    key = c.data.split('_', maxsplit=1)[1]
    await state.update_data(key=key)

    if key == "dating_fun_rate":
        await c.message.answer(
            text=""""
Некоторые люди приходят на Random Coffee встречи, чтобы найти партнёров для будущих проектов и завести полезные контакты, условно назовём это "пользой". А кто-то приходит для расширения кругозора, новых эмоций и открытия чего-то нового, назовём это \"фан\". Какое описание больше подходит тебе?
""",
            reply_markup=dating_fun_rate_markup
        )
    else:
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
    user.profile.__setattr__(s_data["key"], m.text.strip())
    await db_session.commit()


    await m.answer(
        text="Ваш обновленный профиль:\n\n" + get_account_description(
            rating=user.profile.rating,
            user_name=user.profile.name,
            reg_date=user.register_date,
            interests=user.profile.interests,
        ),
        reply_markup=account_manage_markup
    )

@connection
async def update_fun_rate(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession, *args):
    await state.clear()
    fun_rate = int(c.data.split('_')[1])

    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)
    user.profile.dating_fun_rate = fun_rate
    await db_session.commit()

    await c.message.answer("Параметр успешно изменён!")
    await c.answer()


def register_account_handlers(dp: Dispatcher):
    dp.callback_query.register(send_account_info, F.data == "lk")
    dp.callback_query.register(ask_what_to_change, F.data == "update_profile")
    dp.callback_query.register(ask_value, F.data.startswith("change_"), StateFilter(UpdateProfileFSM.key_state))
    dp.message.register(update_value, StateFilter(UpdateProfileFSM.value_state))
    dp.callback_query.register(update_fun_rate, F.data.startswith("funrate_"), StateFilter(UpdateProfileFSM.value_state))
