from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext

from sqlalchemy.ext.asyncio import AsyncSession



from database.dao import UserDAO, InitiativeDAO
from database.utils import connection

from fsm.user.private import CreateInitiativeFSM

from markups.user.events import get_take_part_in_event_markup
from markups.admin.event_manage import get_verify_inititative_markup

from text import get_initiative_text

from config import chat_settings

from utils.date import validate_date_time
from utils.enums import EventType


async def ask_date(c: types.CallbackQuery, state: FSMContext):

    await state.set_state(CreateInitiativeFSM.date_state)

    await c.message.answer(
        "Введите дату и время мероприятия в формате ДД-ММ-ГГГГ чч:мм"
    )

    await c.answer()


async def ask_place(m: types.Message, state: FSMContext):
    date = validate_date_time(m.text.strip())

    if not date:
        await m.answer("❗Неверный формат! Попробуйте еще раз")
        return 1

    await state.update_data(datetime=date)
    await state.set_state(CreateInitiativeFSM.place_state)

    await m.answer(
        "Укажите место встречи"
    )


async def ask_activity_type(m: types.Message, state: FSMContext):
    await state.set_state(CreateInitiativeFSM.activity_type_state)
    await state.update_data(place=m.text.strip()[:200])

    await m.answer(
        "Укажите тип активности"
    )


async def ask_comment(m: types.Message, state: FSMContext):
    await state.set_state(CreateInitiativeFSM.comment_state)
    await state.update_data(activity_type=m.text.strip())
    await m.answer("Введите небольшой комментарий-описание о вашей инициативе")


@connection
async def create_initiative(m: types.Message, state: FSMContext, db_session, *args):
    s_data = await state.get_data()
    await state.clear()

    user = await UserDAO.get_obj(db_session, telegram_id=m.from_user.id)

    initiative = await InitiativeDAO.add(
        db_session,
        date_time=s_data['datetime'],
        place=s_data['place'],
        description=m.text.strip(),
        activity_type=s_data['activity_type'],
        creator_id=user.id
    ) 

    await m.bot.send_message(
        chat_id=chat_settings.ADMIN_CHAT_ID,
        text="Новая заявка на публикацию инициативы👇"
    )
    await m.bot.send_message(
        chat_id=chat_settings.ADMIN_CHAT_ID,
        text=get_initiative_text(
            s_data['datetime'],
            s_data['place'],
            m.text.strip(),
            s_data['activity_type']
        ),
        reply_markup=get_verify_inititative_markup(initiative_id=initiative.id)
    )

    await m.answer(
        """Заявка на публикацию вашей инициативы отправлена администраторам.
Вы будете уведомлены об их ответе"""
    )


def register_create_initiative_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_date, F.data == "create_initiative")
    dp.message.register(ask_place, StateFilter(CreateInitiativeFSM.date_state))
    dp.message.register(ask_comment, StateFilter(CreateInitiativeFSM.place_state))
    dp.message.register(create_initiative, StateFilter(CreateInitiativeFSM.comment_state))
