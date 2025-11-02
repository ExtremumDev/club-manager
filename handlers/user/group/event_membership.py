from aiogram import types, Dispatcher, F
from aiogram.exceptions import TelegramForbiddenError


from datetime import datetime


from sqlalchemy.ext.asyncio import AsyncSession


from filters.chat_filters import GroupFilter

from database.dao import MembersEventDAO, EventMembershipDAO, UserDAO

from utils.enums import EventType

from text import get_event_name


@connection
async def user_request_membership(c: types.CallbackQuery, db_session: AsyncSession):
    a, event_id, event_type = c.data.split('_')

    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)

    if not user:
        user = await UserDAO.register_user(
            session=db_session,
            telegram_id=c.from_user.id,
            username=c.from_user.username,
            has_bot_chat=False
        )

    match (event_type):
        case EventType.INITIATIVE:

            pass
        case EventType.FRENCH_CLUB | EventType.BUISNESS_MEETS | EventType.WOMEN_MEETS:
            event = await MembersEventDAO.get_obj(db_session, id=event_id)

            if event:
                if datetime.now() < event.date_time:
                    user_membership = await EventMembershipDAO.get_obj(
                        db_session,
                        user_id=user.id,
                        event_id=event.id

                    )

                    if not user_membership:


                        if event.members_left > 0:
                            event.members_left -= 1
                            is_memnber_of_event = True
                            text = "Вы успешно записались на мероприятие!"
                        else:
                            is_memnber_of_event = False
                            text = "На мероприятии не осталось свободных мест. Вы в листе ожидания"

                        await EventMembershipDAO.add(
                            db_session,
                            user_id=user.id,
                            event_id=event.id,
                            is_member=is_memnber_of_event
                        )

                        await c.answer(
                            text,
                            show_alert=True
                        )
                    else:
                        await c.answer(
                            "Вы уже участвуете в этом мероприятии",
                            show_alert=True
                        )
                else:
                    await c.answer("Мероприятие уже прошло!", show_alert=True)

            else:
                await c.answer("Ошибка: мероприятие не найдено", show_alert=True)
                await c.message.edit_reply_markup(reply_markup=None)

    await db_session.commit()



@connection
async def user_cancel_membership(c: types.CallbackQuery, db_session: AsyncSession):
    a, event_id, event_type = c.data.split('_')

    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)

    if not user:
        user = await UserDAO.register_user(
            session=db_session,
            telegram_id=c.from_user.id,
            username=c.from_user.username,
            has_bot_chat=False
        )

    match (event_type):
        case EventType.INITIATIVE:

            pass
        case EventType.FRENCH_CLUB | EventType.BUISNESS_MEETS | EventType.WOMEN_MEETS:
            event = await MembersEventDAO.get_obj(db_session, id=event_id)

            if event:
                if datetime.now() < event.date_time:
                    user_membership = await EventMembershipDAO.get_obj(
                        db_session,
                        user_id=user.id,
                        event_id=event.id

                    )

                    if user_membership:
                        await db_session.delete(user_membership)

                        if event.members_left == 0:
                            last_in_waiting = await EventMembershipDAO.get_first_member_in_waiting(
                                db_session,
                                event.id
                            )

                            if last_in_waiting:
                                last_in_waiting.is_memeber = True

                                try:
                                    await c.bot.send_message(
                                        chat_id=last_in_waiting.user.telegram_id,
                                        text=f"""
Вы теперь являетесь участником мероприятия {get_event_name(event_type)} {last_in_waiting.event.date_time.str}"""
                                    )
                                except TelegramForbiddenError:
                                    pass
                        

                        await c.answer(
                            "Вы успешно отказались от участия в мероприятии",
                            show_alert=True
                        )
                    else:
                        await c.answer(
                            "Вы еще не участвуете в данном мероприятии, нажмите на кнопку \"Присоединиться\"",
                            show_alert=True
                        )
                else:
                    await c.answer("Мероприятие уже прошло!", show_alert=True)
            else:
                await c.answer("Ошибка: мероприятие не найдено", show_alert=True)
                await c.message.edit_reply_markup(reply_markup=None)
    await db_session.commit()


def register_event_membership_handlers(dp: Dispatcher):
    dp.callback_query.register(
        user_request_membership,
        GroupFilter(),
        F.data.startswith("takepevent_"),
    )

    dp.callback_query.register(
        user_cancel_membership,
        GroupFilter(),
        F.data.startswith("cancelpevent_")
    )
