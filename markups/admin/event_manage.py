from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_verify_inititative_markup(initiative_id) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="✅ Одобрить инициативу",
                callback_data=f"verifinit_{initiative_id}_y"
            )],
            [InlineKeyboardButton(
                text="❌ Отклонить инициативу",
                callback_data=f"verifinit_{initiative_id}_n"
            )]
        ]
    )

def get_event_type_markup(prefix: str = ''):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇫🇷 Разговорный французский клуб",
                    callback_data=f"{prefix}eventtype_0"
                )
            ],
            [InlineKeyboardButton(
                text="💼 Мастермайнды / Бизнес-встречи",
                callback_data=f"{prefix}eventtype_2"
            )],
            [InlineKeyboardButton(
                text="☕️ Женские психологические встречи",
                callback_data=f"{prefix}eventtype_3"
            )],
            [InlineKeyboardButton(
                text=" 🎲 Настольные игры",
                callback_data=f"{prefix}eventtype_1"
            )]
        ]
    )


def get_events_list_markup(events: list):
    inline_keyboard = []

    for e in events:
        inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=e.date_time,
                    callback_data=f"eventm_{e.id}"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )

def get_event_manage_markup(event_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Добавить участника",
                callback_data=f"addmember_{event_id}"
            )]
        ]
    )
