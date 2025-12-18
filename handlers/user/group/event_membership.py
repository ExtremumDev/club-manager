from aiogram import types, Dispatcher, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ChatType


from datetime import datetime


from sqlalchemy.ext.asyncio import AsyncSession

from config import settings, chat_settings
from filters.chat_filters import GroupFilter

from database.dao import MembersEventDAO, EventMembershipDAO, UserDAO
from database.utils import connection

from utils.enums import EventType


async def notice_user_about_seats_left(original_message: types.Message, members_left: int):
    # Notice user about seats left

    notice = False # If need notification (Only when certain values)

    if members_left == 1:
        notice = True
        notification_message = "Последний шанс попасть в историю мафии! Только 1 место осталось!"
    elif members_left == 5:
        notice = True
        notification_message = "Каких то 5 мест всего осталось!"
    elif members_left == 10:
        notice = True
        notification_message = "Пока вы не спешили осталось 10 мест на игру!"
    elif members_left == 15:
        notice = True
        notification_message = "ИЗОБИЛИЕ! Целых 15 мест свободны! Разбирайте! (лес рук)"

    if notice:
        await original_message.reply(
            text=notification_message
        )



@connection
async def user_request_membership(c: types.CallbackQuery, db_session: AsyncSession):
    c_data = c.data.split('_')
    event_id, event_type = c_data[1], c_data[2]
    event_type = EventType(int(event_type))

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
            event = await MembersEventDAO.get_obj(db_session, id=int(event_id))

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
                            is_member_of_event = True
                            text = "Вы успешно записались на мероприятие!"
                        else:
                            is_member_of_event = False
                            text = "На мероприятии не осталось свободных мест. Вы в листе ожидания"

                        await EventMembershipDAO.add(
                            db_session,
                            user_id=user.id,
                            event_id=event.id,
                            is_member=is_member_of_event
                        )

                        new_message_text = EventType(event.event_type).get_card_text(
                            **event.model_to_dict()
                        )

                        if len(c_data) <= 3:  # If it was not a button in week's poster
                            await c.message.edit_text(
                                text=new_message_text,
                                reply_markup=c.message.reply_markup
                            )

                        if c.message.chat.type == ChatType.PRIVATE:
                            try:
                                await c.bot.edit_message_text(
                                    text=new_message_text,
                                    chat_id=chat_settings.GROUP_ID,
                                    message_id=event.info_message_id
                                )
                            except TelegramBadRequest: # if message not found
                                pass
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
    event_type = EventType(int(event_type))

    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)

    if not user:
        user = await UserDAO.register_user(
            session=db_session,
            telegram_id=c.from_user.id,
            username=c.from_user.username,
            has_bot_chat=False
        )

    match (event_type):
        
        case EventType.FRENCH_CLUB | EventType.BUISNESS_MEETS | EventType.WOMEN_MEETS | EventType.TABLE_GAMES:
            event = await MembersEventDAO.get_obj(db_session, id=int(event_id))

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
                                last_in_waiting.is_member = True

                                try:
                                    await c.bot.send_message(
                                        chat_id=last_in_waiting.user.telegram_id,
                                        text=f"""
Вы теперь являетесь участником мероприятия {EventType(event.event_type).get_event_name()} {last_in_waiting.event.date_time.strftime("%d-%m-%Y %H:%M")}"""
                                    )
                                except TelegramBadRequest:
                                    pass
                            else:
                                event.members_left += 1
                        else: 
                            event.members_left += 1

                        alert_message = "Отмена учтена, место снова свободно! Ждем на следующую встречу🫶"

                        if event_type == EventType.TABLE_GAMES:
                            time_difference = event.date_time - datetime.now()

                            # If user cancel partition <24h before event - increase rating
                            if time_difference.days == 0:
                                await UserDAO.change_user_rating(db_session, c.from_user.id, -1)
                                alert_message = "Ты решил отменить участие менее чем за сутки? 😬 Минус 1 балл!"

                        new_message_text = EventType(event.event_type).get_card_text(
                            **event.model_to_dict()
                        )

                        await c.message.edit_text(
                            text=new_message_text,
                            reply_markup=c.message.reply_markup
                        )

                        if c.message.chat.type == ChatType.PRIVATE:
                            await c.bot.edit_message_text(
                                text=new_message_text,
                                chat_id=chat_settings.GROUP_ID,
                                message_id=event.info_message_id,
                                reply_markup=c.message.reply_markup
                            )
                        await c.answer(
                            alert_message,
                            show_alert=True
                        )

                        if event_type == EventType.TABLE_GAMES:
                            await notice_user_about_seats_left(c.message, event.members_left)

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


@connection
async def player_came_on_game(c: types.CallbackQuery, db_session: AsyncSession):
    event_id = c.data.split('_')[1]

    user = await UserDAO.get_obj(db_session, telegram_id=c.from_user.id)

    if not user:
        user = await UserDAO.register_user(
            session=db_session,
            telegram_id=c.from_user.id,
            username=c.from_user.username,
            has_bot_chat=False
        )

    event = await MembersEventDAO.get_obj(
        db_session,
        id=event_id
    )

    if event:
        now = datetime.now()
        if now > event.date_time:
            user_membership = await EventMembershipDAO.get_obj(
                db_session,
                user_id=user.id,
                event_id=event_id
            )
            if user_membership:
                if not user_membership.is_come:
                    if user_membership.is_member:
                        user_membership.is_come = True
                        await UserDAO.change_user_rating(
                            db_session,
                            c.from_user.id,
                            1
                        )

                        await c.answer(
                            "✅ Ваше присутствие учтено"
                        )
                    else:
                        await c.answer(
                            "Вы не можете участвовать в этом мероприятии!"
                        )
                else:
                    await c.answer(
                        "Вы уже отметились!",
                        show_alert=True
                    )
            else:
                await c.answer(
                    "Вы не участвуете в этом мероприятии!"
                )
        else:
            await c.answer(
                "Мероприятие еще не началось",
                show_alert=True
            )
    else:
        await c.answer(
            "Событие не найдено",
            show_alert=True
        )
    await db_session.commit()


def register_event_membership_handlers(dp: Dispatcher):
    dp.callback_query.register(
        user_request_membership,
        F.data.startswith("takepevent_"),
    )

    dp.callback_query.register(
        user_cancel_membership,
        GroupFilter(),
        F.data.startswith("cancelpevent_")
    )
    dp.callback_query.register(
        player_came_on_game,
        GroupFilter(),
        F.data.startswith("cameongame_")
    )
