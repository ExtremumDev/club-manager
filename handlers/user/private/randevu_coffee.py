from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

from sqlalchemy import delete

from filters.user_filters import AdminFilter

from database.utils import connection
from database.dao import UserDAO

from markups.user.randevu import get_randevu_manage_markup

from utils.paging.user_events_paging import UserEventsPaging

from utils.enums import EventType

def get_randevu_settings_text(randevu_notifications: bool):
    if randevu_notifications:
        return "У вас включено получение предложений о встрече. Чтобы выключить👇"
    else:
        return "У вас сейчас выключено получение предложений о встрече. Чтобы включить👇"


@connection
async def send_coffe_info(c: types.CallbackQuery, db_session, *args):
    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)

    await c.answer()
    await c.message.answer(
        text=get_randevu_settings_text(user.randevu_notifications),
        reply_markup=get_randevu_manage_markup(user.randevu_notifications)
    )


@connection
async def switch_mode(c: types.CallbackQuery, db_session, *args):
    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)
    new_mode = int(c.data.split('_')[1])

    user.randevu_notifications = new_mode

    await db_session.commit()

    if new_mode: # new_mode == 1 (turn on)
        text = "Теперь вы будете получать предложения о встречах, пока не выключите их обратно"
    else: # turn off
        text = "Вы не больше получите предложения о встречах, пока не включите их обратно"

    await c.message.edit_text(
        text=get_randevu_settings_text(new_mode)
    )
    await c.message.edit_reply_markup(
        reply_markup=get_randevu_manage_markup(new_mode)
    )
    await c.answer(
        text=text,
        show_alert=True
    )



def register_randevu_handlers(dp: Dispatcher):
    dp.callback_query.register(send_coffe_info, F.data == "randevu-coffee")
    dp.callback_query.register(switch_mode, F.data.startswith("randevu_"))
