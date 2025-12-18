from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.enums import EventType


def get_take_part_in_event_markup(event_id: int, event_type: EventType):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➕ Присоединиться",
                    callback_data=f"takepevent_{event_id}_{event_type}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отменить участие",
                    callback_data=f"cancelpevent_{event_id}_{event_type}"
                )
            ]
        ]
    )

    if event_type == EventType.TABLE_GAMES:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="Я пришел на игру",
                    callback_data=f"cameongame_{event_id}"
                )
            ]
        )

    return keyboard


def take_part_in_week_events_markup(events_id: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Записаться на мероприятия", callback_data="manytakep_" + events_id)]
        ]
    )
