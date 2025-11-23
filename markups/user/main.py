from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from markups.user.account import registration_skip_step_markup, sex_choice_markup

main_user_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="👤 Мой профиль",
                callback_data="lk"
            )
        ],
        [
            InlineKeyboardButton(
                text="☕️ Рандеву-кофе",
                callback_data="randevu-coffee"
            )
        ],
        [
            InlineKeyboardButton(
                text="Посмотреть афишу",
                callback_data="poster"
            )
        ],
    ]
)


