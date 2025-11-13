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
                text="💡 Создать инициативу",
                callback_data="create_initiative"
            )
        ],
        [
            InlineKeyboardButton(
                text="💌 Знакомства и общение",
                callback_data="dating"
            )
        ],
        [
            InlineKeyboardButton(
                text="☕️ Рандеву-кофе",
                callback_data="randevu_coffee"
            )
        ],
        [
            InlineKeyboardButton(
                text="Предложить активность",
                callback_data="suggest_activity"
            )
        ]
    ]
)


