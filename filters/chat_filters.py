from aiogram import types


from config import chat_settings


class GroupFilter:

    def __call__(self, event: types.CallbackQuery | types.Message):
        if isinstance(event, types.CallbackQuery):
            
            return event.message.chat.id == chat_settings.GROUP_ID
        else:
            print(event.chat.id)
            return event.chat.id == chat_settings.GROUP_ID
