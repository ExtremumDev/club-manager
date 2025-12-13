from typing import LiteralString

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


async def ask_profile_photo(c: types.CallbackQuery, state: FSMContext):
    await state.set_state(CreateDatingProfileFSM.profile_photo_state)

    await c.message.answer(
        "Пришлите фотографию для своей анкеты"
    )
    await c.answer()


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


@connection
async def send_first_profile(c: types.CallbackQuery, db_session: AsyncSession, *args):
    profiles = await DatingProfileDAO.get_profiles_for_user(db_session=db_session, user_id=c.from_user.id)

    if profiles:
        profile = profiles[0]

        await c.message.answer_photo(
            photo=profile.photo,
            caption=get_dating_profile_descr(
                name=profile.user.profile.name,
                social_link=profile.social_link,
                interests=profile.interests
            ),
            reply_markup=get_dating_profile_markup(profile.id, 0)
        )

        await c.answer()
    else:
        await c.answer("Не найдено анект, попробуйте в другой раз", show_alert=True)


@connection
async def next_profile(c: types.CallbackQuery, db_session: AsyncSession, *args):
    page = int(c.data.split('_')[1])

    profiles = await DatingProfileDAO.get_profiles_for_user(db_session=db_session, user_id=c.from_user.id)

    if profiles:
        if abs(page) >= len(profiles):
            page = 0

        profile = profiles[0]

        await c.message.edit_media(
            media=types.InputMediaPhoto(
                media=profile.photo,
                caption=get_dating_profile_descr(
                    name=profile.user.profile.name,
                    social_link=profile.social_link,
                    interests=profile.interests,
                ),
            )
        )

        await c.message.edit_reply_markup(
            reply_markup=get_dating_profile_markup(profile.id, page)
        )

        await c.answer()
    else:
        await c.answer("Не найдено анект, попробуйте в другой раз", show_alert=True)



def register_dating_handlers(dp: Dispatcher):
    dp.callback_query.register(what_to_do, F.data == "dating")
    dp.callback_query.register(ask_profile_photo, F.data == "create_dating_profile")
    dp.message.register(ask_descr, StateFilter(CreateDatingProfileFSM.profile_photo_state))
    dp.message.register(ask_interests, StateFilter(CreateDatingProfileFSM.description_state))
    dp.message.register(ask_goal, StateFilter(CreateDatingProfileFSM.interests_state))
    dp.callback_query.register(
        create_dating_profile,
        F.data.startswith("dgoal_"),
        StateFilter(CreateDatingProfileFSM.goal_state)
    )

    # Listing

    dp.callback_query.register(send_first_profile, F.data == "watch_dating")
    dp.callback_query.register(next_profile, F.data.startswith("nextprofile_"))
