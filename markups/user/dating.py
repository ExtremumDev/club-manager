from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



def get_dating_profile_markup(profile_id, page: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Хочу познакомиться", callback_data=f"like_{profile_id}")],
            [
                InlineKeyboardButton(text="<-", callback_data=f"nextprofile_{page - 1}"),
                InlineKeyboardButton(text="->", callback_data=f"nextprofile_{page + 1}")
            ]
        ]
    )


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
