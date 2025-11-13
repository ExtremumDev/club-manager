from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton



account_manage_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Редактикровать профиль", callback_data="update_profile")],
        [InlineKeyboardButton(text="Мои мероприятия", callback_data="my_events")]
    ]
)
registration_skip_step_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Пропустить", callback_data="skip_step")
        ]
    ]
)
sex_choice_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Мужской", callback_data="male"),
            InlineKeyboardButton(text="Женский", callback_data="fem")
        ]
    ]
)
sex_choice_markup.inline_keyboard.extend(registration_skip_step_markup.inline_keyboard)

update_profile_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Имя", callback_data="change_name"),
            InlineKeyboardButton(text="Псевдоним", callback_data="change_alias")
        ],
        [
            InlineKeyboardButton(text="Интересы",callback_data="change_interests")
        ]
    ]
)
