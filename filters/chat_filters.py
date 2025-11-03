from aiogram import types


from utils.logger import get_bot_logger

from config import chat_settings


class GroupFilter:

    def __call__(self, event: types.CallbackQuery | types.Message):
        if isinstance(event, types.CallbackQuery):
            
            return event.message.chat.id == chat_settings.GROUP_ID
        else:
            get_bot_logger().info(str(event.chat.id) + "\n\n\n\n\n")
            return event.chat.id == chat_settings.GROUP_ID
