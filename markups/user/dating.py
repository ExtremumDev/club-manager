from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


dating_actions_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Создать анкету", callback_data="create_dating_profile")],
        [InlineKeyboardButton(text="Смотреть анкеты", callback_data="watch_dating")]
    ]
)


dating_goal_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Друзья", callback_data="dgoal_0")],
        [InlineKeyboardButton(text="Коллеги", callback_data="dgoal_1")],
        [InlineKeyboardButton(text="Партнёры", callback_data="dgoal_2")]
    ]
)
