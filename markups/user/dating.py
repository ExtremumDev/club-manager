from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_random_user_markup(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Написать пользователю", callback_data=f"contactuser_{user_id}")]
        ]
    )


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

def get_randevu_accept_markup(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data=f"acceptr_{user_id}")],
            [InlineKeyboardButton(text="Нет", callback_data="decline_randevu")]
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

dating_fun_rate_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="100% фан", callback_data="funrate_100")],
        [InlineKeyboardButton(text="75% фан, 25% польза", callback_data="funrate_75")],
        [InlineKeyboardButton(text="50% фан, 50% польза", callback_data="funrate_50")],
        [InlineKeyboardButton(text="25% фан, 75% польза", callback_data="funrate_25")],
        [InlineKeyboardButton(text="100% польза", callback_data="funrate_0")],
    ]
)
