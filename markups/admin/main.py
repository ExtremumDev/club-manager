from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from markups.user.main import main_user_markup


main_markup_for_admin = InlineKeyboardMarkup(
    inline_keyboard=main_user_markup
)
main_markup_for_admin.inline_keyboard.extend(
    [
        [
            InlineKeyboardButton(
                text="Админ-панель",
                callback_data="admin_panel"
            )
        ]
    ]
)


main_admin_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Создать событие", callback_data="add_event")],
        [InlineKeyboardButton(text="Управление событиями", callback_data="manage_events")],
        [InlineKeyboardButton(text="✉️ Новая рассылка пользователям", callback_data="mailing")],
        [InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="back_to_menu")]
    ]
)


confirm_mailing_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data="mail_confirm"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отменить создание рассылки",
                callback_data="mail_canc"
            )
        ]
    ]
)
