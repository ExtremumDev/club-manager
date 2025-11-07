from typing import List, Any, Dict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, asc, update
from sqlalchemy.orm import joinedload

from .models import User, MemberEvent, EventMembership, Initiative


class BaseDAO:
    model = None

    @classmethod
    async def add(cls, session: AsyncSession, **values):
        new_instance = cls.model(**values)
        session.add(new_instance)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instance

    @classmethod
    async def get_obj(cls, session: AsyncSession, **values):
        query = select(cls.model).filter_by(**values)

        result = await session.execute(query)
        obj = result.scalar_one_or_none()
        return obj

    @classmethod
    async def add_many(cls, session: AsyncSession, instances: List[Dict[str, Any]]):
        new_instances = [cls.model(**values) for values in instances]
        session.add_all(new_instances)
        try:
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            raise e
        return new_instances


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def register_user(
        cls,
        session: AsyncSession,
        telegram_id: int,
        username: str,
        has_bot_chat: bool,
        is_admin: bool = False
    ) -> User:
        return await cls.add(
            session,
            telegram_id=telegram_id,
            telegram_username=username,
            has_private=has_bot_chat
        )

    @classmethod
    async def get_active_users(cls, session: AsyncSession):
        query = select(cls.model).filter_by(has_private=True)

        result = await session.execute(query)

        records = result.scalars().all()

        return records

    @classmethod
    async def change_user_rating(cls, session: AsyncSession, telegram_id: int, change: int):
        query = update(cls.model).where(User.telegram_id==telegram_id).values(
            rating=User.rating + change
        )

        await session.execute(query)


class MembersEventDAO(BaseDAO):
    model = MemberEvent

    @classmethod
    async def create_event(
        cls,
        db_session: AsyncSession,
        date_time,
        place,
        description,
        members_limit,
        event_type,
        activity_name
    ):
        new_event = cls.model(
            date_time=date_time,
            place=place,
            description=description,
            members_limit=members_limit,
            members_left=members_limit,
            event_type=event_type,
            activity_name=activity_name
        )
        db_session.add(new_event)
        await db_session.flush()
        return new_event


    @classmethod
    async def get_event_with_members(cls, db_session: AsyncSession, event_id: int):
        query = select(MemberEvent).options(
            joinedload(
                MemberEvent.members
            ).joinedload(
                EventMembership.user
            )
        ).filter_by(MemberEvent.id == event_id)

        res = await db_session.execute(query)
        event = res.scalar_one_or_none()
        return event

    @classmethod
    async def get_all_events_by_type(cls, db_session: AsyncSession, event_type):
        query = select(MemberEvent).filter_by(event_type=event_type)
        res = await db_session.execute()
        return await res.scalars().all()



class EventMembershipDAO(BaseDAO):
    model = EventMembership


    @classmethod
    async def get_first_member_in_waiting(
        cls,
        db_session: AsyncSession,
        event_id
    ) -> EventMembership:
        """Returns first member who clicked the participate button
        but there wasn't enough members left"""

        query = select(cls.model).join(User).where(
            User.id == EventMembership.user_id
        ).filter_by(
            event_id=event_id,
            is_member=False
        ).order_by(asc(EventMembership.created_ad))

        result = await db_session.execute(query)
        first_waiting = result.first()
        return first_waiting


class InitiativeDAO(BaseDAO):
    model = Initiative
