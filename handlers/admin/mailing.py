from aiogram import types, Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatType
from aiogram.exceptions import TelegramForbiddenError


from asyncio import sleep


from filters.user_filters import AdminFilter

from sqlalchemy.ext.asyncio import AsyncSession

from fsm.admin.mailing import CreateMailingFSM

from markups.admin.main import confirm_mailing_markup

from database.dao import UserDAO
from database.utils import connection


async def ask_main_message(c: types.CallbackQuery, state: FSMContext):
    await c.answer()

    await state.set_state(CreateMailingFSM.message_state)
    await c.message.answer(
        "Введите основное сообщение рассылки"
    )


async def ask_photo(m: types.Message, state: FSMContext):
    await state.set_state(CreateMailingFSM.photo_state)
    await state.update_data(message=m.text.strip())

    await m.answer(
        """Пришлите фотографию, которая будет отправлена вместе с текстом
Если картинка не нужна, то пришлите любой текст"""
    )


async def confirm_mailing(m: types.Message, state: FSMContext):
    await state.set_state(CreateMailingFSM.confirm_state)

    if m.photo:
        await state.update_data(photo=m.photo[0].file_id)
    else:
        await state.update_data(photo=None)

    s_data = await state.get_data()

    if m.photo:
        await m.answer_photo(
            m.photo.file_id,
            caption=s_data['message']
        )
    else:
        await m.answer(
            s_data['message']
        )

    await m.answer(
        "Так ваша рассылка будет выглядеть для пользователей. Завершить создание и разослать?",
        reply_markup=confirm_mailing_markup
    )


@connection
async def get_confirmation(c: types.CallbackQuery, state: FSMContext, db_session, *args):
    confirm = c.data.split('_')[1]

    await c.answer()

    if confirm == "canc":
        await state.clear()

        await c.message.answer(
            "Создание рассылки отменено"
        )
    else:
        s_data = await state.get_data()
        await state.clear()

        photo_id = s_data['photo']
        message_text = s_data['message']

        is_photo = bool(photo_id)

        await c.message.answer("Рассылка успешно отправляется пользователям!")

        users = await UserDAO.get_active_users(db_session)
        
        i = 0
        
        for u in users:
            i += 1

            try:
                if is_photo:
                    await c.bot.send_photo(
                        chat_id=u.telegram_id,
                        photo=photo_id,
                        caption=message_text
                    )
                else:
                    await c.bot.send_message(
                        chat_id=u.telegram_id,
                        text=message_text
                    )
            except TelegramForbidden:
                pass
            
            if i % 15 == 0:
                sleep(3)


def regster_create_mailing_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_main_message, F.data == "mailing", AdminFilter())
    dp.message.register(ask_photo, StateFilter(CreateMailingFSM.message_state))
    dp.message.register(confirm_mailing, StateFilter(CreateMailingFSM.photo_state))
    dp.callback_query.register(
        get_confirmation,
        F.data.startswith("mail_"),
        StateFilter(CreateMailingFSM.confirm_state)
    )
