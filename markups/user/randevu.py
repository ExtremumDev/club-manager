from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_randevu_manage_markup(is_turned: bool):
    button: InlineKeyboardButton

    if is_turned:
        button = InlineKeyboardButton(
            text="⏸️ Выключить",
            callback_data="randevu_0"
        )
    else:
        button = InlineKeyboardButton(
            text="Включить",
            callback_data="randevu_1"
        )


    return InlineKeyboardMarkup(
        inline_keyboard=[
            [button]
        ]
    )
