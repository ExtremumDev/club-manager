from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_fallback

from fsm.user.private import RegistrationFSM

from markups.user.main import main_user_markup
from markups.user.account import registration_skip_step_markup, sex_choice_markup

from database.dao import UserDAO, UserProfileDAO
from database.utils import connection

from utils.date import validate_date_time
from utils.enums import Sex


@connection
async def start_cmd(m: types.Message, state: FSMContext, db_session: AsyncSession):
    await state.clear()

    user = await UserDAO.get_obj(db_session, telegram_id=m.from_user.id)
    reg = True
    if not user:
        reg = False
        await UserDAO.register_user(
            db_session, m.from_user.id, m.from_user.username, True
        )
    else:
        if not user.has_private:
            reg = False

    if reg:
        await m.answer(
            "Открыто главное меню",
            reply_markup=main_user_markup
        )
    else:
        await state.set_state(RegistrationFSM.name_state)
        await m.answer_photo(
            photo=types.FSInputFile("image/start_image.jpg"),
            caption="""
Приветстсвую! Я твой помощник в комьюнити RendezVous.\n Давай познакомимся. Как тебя зовут?
"""
        )




async def ask_alias(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer(
        "Отлично! Теперь придумайте себе псеводним"
    )


async def ask_city(m: types.Message, state: FSMContext):
    await state.set_state(RegistrationFSM.city_state)
    await state.update_data(alias=m.text.strip())

    await m.answer("Введите свой город")


async def ask_interests(m: types.Message, state: FSMContext):
    await state.set_state(RegistrationFSM.interests_state)
    await state.update_data(city=m.text)
    await m.answer(
        "Расскажите о своих интересах"
    )


async def ask_birthday(m: types.Message, state: FSMContext):
    await state.set_state(RegistrationFSM.sex_state)
    await state.update_data(interests=m.text)

    await m.answer("Введите свой день рождения в формате дд-мм-гггг")


async def ask_sex(m: types.Message, state: FSMContext):

    date_birthday = validate_date_time(m.text.strip(), "%d-%m-%Y")

    if date_birthday:
        await state.set_state(RegistrationFSM.sex_state)
        await state.update_data(birthday=date_birthday)

        await m.answer("Выберите свой пол (опционально)", reply_markup=sex_choice_markup)
    else:
        await m.answer("Неверный формат даты, попробуйте еще раз")


async def ask_social_link(c: types.CallbackQuery, state: FSMContext):
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
    await finish_registration(m, await state.get_data())


async def skip_social_link(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(social_link=None)
    await c.answer()
    await finish_registration(c.message, await state.get_data())

@connection
async def finish_registration(
    m: types.Message, state_data: dict, db_session: AsyncSession, *args
):

    user = await UserDAO.get_obj(db_session, telegram_id=m.from_user.id)

    user.has_private = True

    profile = await UserProfileDAO.add(
        db_session,
        name=state_data['name'],
        alias=state_data['alias'],
        city=state_data['city'],
        birthday=state_data['birthday'],
        interests=state_data['interests'],
        sex=state_data['sex'],
        social_link=state_data['social_link']
    )

    user.profile = profile

    await db_session.commit()

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

    dp.message.register(ask_alias, StateFilter(RegistrationFSM.name_state))
    dp.message.register(ask_city, StateFilter(RegistrationFSM.alias_state))
    dp.message.register(ask_interests, StateFilter(RegistrationFSM.city_state))
    dp.message.register(ask_birthday, StateFilter(RegistrationFSM.interests_state))
    dp.message.register(ask_sex, StateFilter(RegistrationFSM.birthday_state))
    dp.callback_query.register(ask_social_link, StateFilter(RegistrationFSM.sex_state))
    dp.message.register(get_social_link, StateFilter(RegistrationFSM.social_link_state))
    dp.callback_query.register(
        skip_social_link,
        F.data == "skip_step",
        StateFilter(RegistrationFSM.social_link_state)
    )