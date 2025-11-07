from aiogram import types, Dispatcher, F
from aiogram.enums import ParseMode


from filters.user_filters import AdminFilter

from markups.user.events import get_take_part_in_event_markup

from database.utils import connection
from database.dao import InitiativeDAO

from config import chat_settings

from utils.enums import EventType

from text import get_initiative_text


@connection
async def verify_initiative(c: types.CallbackQuery, db_session, *args):
    a, init_id, verif = c.data.split('_')
    await c.answer()

    initiative = await InitiativeDAO.get_obj(
        db_session,
        id=init_id
    )

    if initiative:
        if initiative.verified:
            await c.message.edit_reply_markup(reply_markup=None)
            await c.answer(
                "Данная иницитива уже одобрена другим администратором!",
                show_alert=True
            )
        else:
            if verif == 'y':
                initiative.verified = True
                m = await c.message.bot.send_message(
                    chat_id=chat_settings.GROUP_ID,
                    message_thread_id=chat_settings.INITIATIVES_THREAD_ID,
                    text=get_initiative_text(
                        initiative.date_time,
                        initiative.place,
                        initiative.description,
                        initiative.activity_type
                    ),
                    reply_markup=get_take_part_in_event_markup(
                        init_id,
                        EventType.INITIATIVE
                    )
                )

                await c.message.bot.send_message(
                    chat_id=initiative.creator.telegram_id,
                    text=f"Ваша инициатива была одобрена администраторами и успешно <a href=\"{m.get_url(include_thread_id=True)}\">опубликована</a>",
                    parse_mode=ParseMode.HTML
                )

            else:
                await db_session.delete(initiative)
                await c.message.bot.send_message(
                    chat_id=initiative.creator.telegram_id,
                    text="❌ Ваша заявка на публикацию инициативы была отклонена администраторами"
                )
            await db_session.commit()



            await c.answer(
                "Заявка на публикацию инициативы успешно одобрена!"
            )

    else:
        await c.message.edit_reply_markup(reply_markup=None)
        await c.answer("Данная инициатива не найдена!", show_alert=True)


def register_manage_initiative_handlers(dp: Dispatcher):
    dp.callback_query.register(
        verify_initiative,
        F.data.startswith("verifinit_"),
        AdminFilter()
    )
