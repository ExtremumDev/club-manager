from apscheduler.triggers.cron import CronTrigger


from aiogram.exceptions import TelegramForbiddenError


import datetime

from utils.enums import EventType

from database.dao import MembersEventDAO
from database.utils import connection

from bot import bot

from scheduler.scheduler import scheduler

from text import (
    two_hours_before_text_buisness, two_hours_before_text_french, two_hours_before_text_women,
    day_before_text_buisness, day_before_text_french, day_before_text_women
)


def setup_event_notifications(
    event_date_time: datetime.datetime,
    event_id: int,
    event_type: EventType
):

    match (event_type):
        case (EventType.FRENCH_CLUB):
            day_before_text = day_before_text_french
            two_hours_before_text = two_hours_before_text_french
        case (EventType.WOMEN_MEETS):
            day_before_text = day_before_text_women
            two_hours_before_text = two_hours_before_text_women
        case (EventType.BUISNESS_MEETS):
            day_before_text = day_before_text_buisness
            two_hours_before_text = two_hours_before_text_buisness

    day_before_datetime = event_date_time - datetime.timedelta(days=1)
    two_hours_before = event_date_time - datetime.timedelta(hours=2)

    scheduler.add_job(
        func=send_event_notification,
        trigger=CronTrigger(
            year=day_before_datetime.year,
            month=day_before_datetime.month,
            day=day_before_datetime.day,
            hour=day_before_datetime.hour,
            minute=day_before_datetime.minute,
            second=day_before_datetime.second
        ),
        kwargs={
            'event_id': event_id,
            'message': day_before_text,
        }
    )

    scheduler.add_job(
        func=send_event_notification,
        trigger=CronTrigger(
            year=two_hours_before.year,
            month=two_hours_before.month,
            day=two_hours_before.day,
            hour=two_hours_before.hour,
            minute=two_hours_before.minute,
            second=two_hours_before.second
        ),
        kwargs={
            'event_id': event_id,
            'message': two_hours_before_text,
        }
    )

@connection
async def send_event_notification(event_id: int, message: str, db_session, *args):
    event = await MembersEventDAO.get_event_with_members(db_session, event_id)

    for u in event.members:
        user = u.user

        try:
            await bot.send_message(
                user.telegram_id,
                text=message
            )
        except TelegramForbiddenError:
            pass
