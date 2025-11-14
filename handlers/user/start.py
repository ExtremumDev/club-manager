from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_fallback

from fsm.user.private import RegistrationFSM
from markups.admin.main import main_markup_for_admin
from markups.user.dating import dating_goal_markup

from markups.user.main import main_user_markup
from markups.user.account import registration_skip_step_markup, sex_choice_markup

from database.dao import UserDAO, UserProfileDAO
from database.utils import connection

from utils.date import validate_date_time
from utils.enums import Sex


@connection
async def start_cmd(m: types.Message, state: FSMContext, db_session: AsyncSession, *args):
    await state.clear()

    user = await UserDAO.get_obj(db_session, telegram_id=m.from_user.id)
    reg = False
    if not user:
        reg = True
        await UserDAO.register_user(
            db_session, m.from_user.id, m.from_user.username, False
        )
    else:
        if not user.has_private:
            reg = True

    if reg:
        await state.set_state(RegistrationFSM.name_state)
        await m.answer_photo(
            photo=types.FSInputFile("images/start_image.jpg"),
            caption="""
Приветстсвую! Я твой помощник в комьюнити RendezVous.\n Давай познакомимся. Как тебя зовут?
"""
        )
    else:
        await m.answer(
            "Открыто главное меню",
            reply_markup=main_user_markup
        )


async def ask_interests(m: types.Message, state: FSMContext):
    await state.set_state(RegistrationFSM.interests_state)
    await state.update_data(name=m.text)
    await m.answer(
        "Расскажите о своих интересах"
    )

async def ask_goal(m: types.Message, state: FSMContext):
    await state.set_state(RegistrationFSM.goal_state)
    await state.update_data(interests=m.text.strip())

    await m.answer(
        "С какой целью хотите найти людей?",
        reply_markup=dating_goal_markup
    )


async def ask_sex(c: types.CallbackQuery, state: FSMContext):

    await state.set_state(RegistrationFSM.sex_state)

    goal_index = int(c.data.split('_')[1])
    goal_markup = c.message.reply_markup
    goal = goal_markup.inline_keyboard[goal_index][0].text

    await state.update_data(goal=goal)
    await c.message.answer("Выберите свой пол (опционально)", reply_markup=sex_choice_markup)


async def ask_social_link(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(RegistrationFSM.social_link_state)
    choice = c.data

    if choice == "skip_step":
        sex = None
    elif choice == "male":
        sex = Sex.MALE
    else:
        sex = Sex.FEMALE
    await state.update_data(sex=sex)

    await c.message.answer(
        "Введите ссылку на свой инстраграм / телеграмм (опционально)",
        reply_markup=registration_skip_step_markup
    )
    await c.answer()


async def get_social_link(m: types.Message, state: FSMContext):
    await state.update_data(social_link=m.text)
    await finish_registration(m, await state.get_data(), user_id=m.from_user.id)


async def skip_social_link(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(social_link=None)
    await c.answer()
    await finish_registration(c.message, await state.get_data(), user_id=c.from_user.id)

@connection
async def finish_registration(
    m: types.Message, state_data: dict, user_id: int, db_session: AsyncSession, *args
):

    user = await UserDAO.get_obj(db_session, telegram_id=user_id)

    user.has_private = True

    profile = await UserProfileDAO.add(
        db_session,
        name=state_data['name'],
        interests=state_data['interests'],
        sex=state_data['sex'],
        social_link=state_data['social_link'],
        goal=state_data['goal']
    )

    user.profile = profile

    await db_session.commit()

    if user.is_admin:

        await m.answer(
            text="Добро пожаловать!",
            reply_markup=main_markup_for_admin
        )
    else:
        await m.answer(
            "Регистрация прошла успешно. Какие ваши дальнейшие действия?",
            reply_markup=main_user_markup
        )


def register_user_start_handlers(dp: Dispatcher):
    dp.message.register(
        start_cmd,
        F.chat.type == ChatType.PRIVATE,
        CommandStart(),
        StateFilter('*')
    )

    dp.message.register(ask_interests, StateFilter(RegistrationFSM.name_state))
    dp.message.register(ask_goal, StateFilter(RegistrationFSM.interests_state))
    dp.callback_query.register(ask_sex, F.data.startswith("dgoal_"), StateFilter(RegistrationFSM.interests_state))
    dp.callback_query.register(ask_social_link, StateFilter(RegistrationFSM.sex_state))
    dp.message.register(get_social_link, StateFilter(RegistrationFSM.social_link_state))
    dp.callback_query.register(
        skip_social_link,
        F.data == "skip_step",
        StateFilter(RegistrationFSM.social_link_state)
    )