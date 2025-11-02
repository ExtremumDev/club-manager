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


event_type_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🇫🇷 Разговорный французский клуб",
                callback_data="createevent_0"
            )
        ],
        [InlineKeyboardButton(
            text="☕️ Женские психологические встречи",
            callback_data="createevent_2"
        )],
        [InlineKeyboardButton(
            text="☕️ Женские психологические встречи",
            callback_data="createevent_3"
        )]
    ]
)
