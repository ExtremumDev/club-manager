from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession

from database.dao import UserDAO, DatingProfileDAO
from database.utils import connection

from markups.user.dating import dating_actions_markup, dating_goal_markup, get_dating_profile_markup

from fsm.user.private import CreateDatingProfileFSM

from text import get_dating_profile_descr
from config import chat_settings


async def what_to_do(c: types.CallbackQuery):
    await c.message.answer(
        "Что хотите сделать?",
        reply_markup=dating_actions_markup
    )
    await c.answer()


async def ask_profile_photo(m: types.Message, state: FSMContext):
    await state.set_state(CreateDatingProfileFSM.profile_photo_state)

    await m.answer(
        "Пришлите фотографию для своей анкеты"
    )


async def ask_descr(m: types.Message, state: FSMContext):

    if m.photo:
        await state.update_data(photo=m.photo[0].file_id)
    else:
        await m.answer("❗Пришлите фотографию")
        return 0


    await state.set_state(CreateDatingProfileFSM.description_state)

    await m.answer(
        "Расскажите немного о себе для анкеты"
    )


async def ask_interests(m: types.Message, state: FSMContext):
    await state.set_state(CreateDatingProfileFSM.interests_state)
    await state.update_data(descr=m.text.strip())

    await m.answer("Расскажите о своих интересах")


async def ask_goal(m: types.Message, state: FSMContext):
    await state.set_state(CreateDatingProfileFSM.goal_state)
    await state.update_data(interests=m.text.strip())

    await m.answer(
        "С какой целью хотите найти людей?",
        reply_markup=dating_goal_markup
    )


@connection
async def create_dating_profile(c: types.CallbackQuery, state: FSMContext, db_session: AsyncSession, *args):
    s_data = await state.get_data()
    await state.clear()

    goal_index = int(c.data.split('_')[1])
    goal_markup = c.message.reply_markup
    goal = goal_markup.inline_keyboard[goal_index][0].text
    await c.answer()

    await DatingProfileDAO.add(
        db_session,
        photo=s_data["photo"],
        description=s_data["descr"],
        interests=s_data["interests"],
        goal=goal
    )

    await c.message.answer("Ваша анкета успешно создана и теперь видна другим пользователям!")


async def send_profiles(c: types.CallbackQuery):




def register_dating_handlers(dp: Dispatcher):
    dp.callback_query.register(what_to_do, F.data == "dating")
    dp.callback_query.register(ask_profile_photo, F.data == "create_dating_profile")
    dp.message.register(ask_descr, StateFilter(CreateDatingProfileFSM.profile_photo_state))
    dp.message.register(create_dating_profile, StateFilter(CreateDatingProfileFSM.description_state))
