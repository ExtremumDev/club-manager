from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType, ContentType

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_fallback

from fsm.user.private import RegistrationFSM
from markups.admin.main import main_markup_for_admin
from markups.user.dating import dating_goal_markup

from markups.user.main import main_user_markup
from markups.user.account import registration_skip_step_markup, sex_choice_markup
from markups.user.dating import dating_fun_rate_markup

from database.dao import UserDAO, UserProfileDAO
from database.utils import connection
from text import get_dating_profile_descr

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
Приветстсвую! Я твой помощник в комьюнити RendezVous.\n\n Давай познакомимся. Как тебя зовут? Напиши имя и фамилию
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
        """
Некоторые люди приходят на Random Coffee встречи, чтобы найти партнёров для будущих проектов и завести полезные контакты, условно назовём это "пользой". А кто-то приходит для расширения кругозора, новых эмоций и открытия чего-то нового, назовём это "фан". Какое описание больше подходит тебе?
""",
        reply_markup=dating_fun_rate_markup
    )


async def ask_sex(c: types.CallbackQuery, state: FSMContext):

    await state.set_state(RegistrationFSM.sex_state)

    fun_rate = int(c.data.split('_')[1])

    await state.update_data(fun_rate=fun_rate)
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
    await state.set_state(RegistrationFSM.photo_state)
    await m.answer(
        "Хочешь установить фото профиля? Если да - пришли фотографию, если нет - нажми кнопку внизу",
        reply_markup=registration_skip_step_markup
    )


async def skip_social_link(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(social_link=None)
    await c.answer()
    await state.set_state(RegistrationFSM.photo_state)
    await c.message.answer(
        "Хочешь установить фото профиля? Если да - пришли фотографию, если нет - нажми кнопку внизу",
        reply_markup=registration_skip_step_markup
    )


async def get_profile_photo(m: types.Message, state: FSMContext):
    await state.update_data(profile_photo=m.photo[0].file_id)
    await finish_registration(m=m, state_data=await state.get_data())


async def skip_profile_photo(c: types.CallbackQuery, state: FSMContext):
    await state.update_data(photo=None)
    await c.answer()
    await finish_registration(m=c.message, state_data=await state.get_data())

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
        dating_fun_rate=state_data['fun_rate'],
        photo=state_data['photo']
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
            """Получилось! 🙌

Теперь ты участник нашего клуба

Вот так будет выглядеть твой профиль в сообщении, которое мы пришлем твоему собеседнику:""",
            reply_markup=main_user_markup
        )

        if profile.photo:
            await m.answer_photo(
                photo=profile.photo,
                caption=get_dating_profile_descr(interests=profile.interests, name=profile.name, social_link=profile.social_link)
            )
        else:
            await m.answer(
                text=get_dating_profile_descr(name=profile.name, social_link=profile.social_link, interests=profile.interests)
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
    dp.callback_query.register(ask_sex, F.data.startswith("funrate_"), StateFilter(RegistrationFSM.interests_state))
    dp.callback_query.register(ask_social_link, StateFilter(RegistrationFSM.sex_state))
    dp.message.register(get_social_link, StateFilter(RegistrationFSM.social_link_state))
    dp.callback_query.register(
        skip_social_link,
        F.data == "skip_step",
        StateFilter(RegistrationFSM.social_link_state)
    )

    dp.message.register(get_profile_photo, StateFilter(RegistrationFSM.photo_state), F.content_type == ContentType.PHOTO)
    dp.callback_query.register(skip_profile_photo, F.data == "skip_step", StateFilter(RegistrationFSM.photo_state))