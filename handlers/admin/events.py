from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter


from datetime import timedelta


from sqlalchemy.ext.asyncio import AsyncSession


from database.dao import MembersEventDAO
from database.utils import connection

from filters.user_filters import AdminFilter

from markups.admin.event_manage import get_event_type_markup
from markups.user.events import get_take_part_in_event_markup

from fsm.admin.events_manage import CreateEventFSM

from text import (
    get_buisness_meet_card_text,
    get_french_club_card_text,
    get_women_meets_card_text,
    get_table_game_card_text
)

from utils.enums import EventType
from utils.date import validate_date_time

from scheduler.event_jobs import setup_event_notifications

from config import chat_settings


async def ask_event_type(c: types.CallbackQuery):
    await c.message.answer(
        "Выберите, событие, которое хотите зарегистрировать",
        reply_markup=get_event_type_markup()
    )
    await c.answer()


async def ask_date_time(c: types.CallbackQuery, state: FSMContext):
    """
    Создание события универсально сразу для разных видов событий
    """
    event_type = EventType(int(c.data.split('_')[1]))
    await state.set_state(CreateEventFSM.date_time_state)
    await state.update_data(event_type=event_type)

    await c.message.answer(
        "Введите дату и время мероприятия в формате ДД-ММ-ГГГГ чч:мм"
    )
    await c.answer()


async def ask_place(m: types.Message, state: FSMContext):
    date_time = validate_date_time(m.text.strip())
    
    if not date_time:
        await m.answer("Неверный формат даты и времени, попробуйте еще раз")
        return 1

    await state.update_data(date_time=date_time)
    await state.set_state(CreateEventFSM.place_state)

    await m.answer("Введите адрес мероприятия")



async def ask_description(m: types.Message, state: FSMContext):
    await state.update_data(place=m.text.strip())
    

    s_data = await state.get_data()
    if s_data['event_type'] == EventType.TABLE_GAMES:
        await state.set_state(CreateEventFSM.game_name_state)
        await m.answer(
            "Введите название игры"
        )
    else:
        await state.set_state(CreateEventFSM.descr_state)
        await m.answer(
            "Придумайте описание для встречи"
        )


async def get_game_name(m: types.Message, state: FSMContext):
    await state.set_state(CreateEventFSM.descr_state)
    await state.update_data(game_name=m.text.strip())

    await m.answer(
        "Придумайте описание для встречи"
    )


async def get_description(m: types.Message, state: FSMContext):
    await state.update_data(descr=m.text.strip())

    s_data = await state.get_data()

    if s_data['event_type'] == EventType.WOMEN_MEETS:
        await state.clear()
        s_data['members_limit'] = 10
        await create_event(m.bot, m.from_user.id, s_data)
    else:
        await state.set_state(CreateEventFSM.members_limit_state)
        await m.answer("Введите лимит мест на мероприятие")


async def get_members_limit(m: types.Message, state: FSMContext):
    try:
        members_limit = int(m.text)

        await state.update_data(members_limit=members_limit)
        await create_event(m.bot, m.from_user.id, await state.get_data())
    except ValueError:
        await m.answer("❗Необходимо ввести число")


@connection
async def create_event(bot, creator_id: int, state_data: dict, db_session: AsyncSession):

    new_event = await MembersEventDAO.create_event(
        db_session,
        state_data['date_time'],
        state_data['place'],
        state_data['descr'],
        state_data['members_limit'],
        state_data['event_type'],
        state_data.get("game_name", None)
    )

    match (state_data['event_type']):
        case (EventType.BUISNESS_MEETS):
            thread_id = chat_settings.BUISNESS_MEETS_THREAD_ID
            message_text = get_buisness_meet_card_text(
                date_time=state_data['date_time'],
                place=state_data['place'],
                description=state_data['descr'],
                members_left=state_data['members_limit']
            )
        case (EventType.WOMEN_MEETS):
            thread_id = chat_settings.WOMEN_MEETS_THREAD_ID
            message_text = get_women_meets_card_text(
                date_time=state_data['date_time'],
                place=state_data['place'],
                description=state_data['descr'],
                members_left=state_data['members_limit']
            )
        case (EventType.FRENCH_CLUB):
            thread_id = chat_settings.FRENCH_CLUB_THREAD_ID
            message_text = get_french_club_card_text(
                date_time=state_data['date_time'],
                place=state_data['place'],
                description=state_data['descr'],
                members_left=state_data['members_limit']
            )
        case (EventType.TABLE_GAMES):
            thread_id = chat_settings.TABLE_GAME_THREAD_ID
            message_text = get_table_game_card_text(
                date_time=state_data['date_time'],
                place=state_data['place'],
                description=state_data['descr'],
                members_left=state_data['members_limit'],
                game_name=state_data['game_name']
            )

    await bot.send_message(
        chat_id=chat_settings.GROUP_ID,
        message_thread_id=thread_id,
        text=message_text,
        reply_markup=get_take_part_in_event_markup(
            new_event.id,
            state_data['event_type'].value
        )
    )

    await db_session.commit()

    if state_data['event_type'] != EventType.TABLE_GAMES:
        setup_event_notifications(
            event_date_time=state_data['date_time'],
            event_id=new_event.id,
            event_type=state_data['event_type']
        )

    await bot.send_message(
        creator_id,
        "Событие успешно создано"
    )


def register_create_event_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_event_type, F.data == "add_event")
    dp.callback_query.register(ask_date_time, F.data.startswith("eventtype_"))
    dp.message.register(ask_place, StateFilter(CreateEventFSM.date_time_state))
    dp.message.register(ask_description, StateFilter(CreateEventFSM.place_state))
    dp.message.register(get_game_name, StateFilter(CreateEventFSM.game_name_state))
    dp.message.register(get_description, StateFilter(CreateEventFSM.descr_state))
    dp.message.register(
        get_members_limit,
        StateFilter(CreateEventFSM.members_limit_state)
    )
