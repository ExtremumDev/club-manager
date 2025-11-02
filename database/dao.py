from typing import List, Any, Dict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, asc

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
        has_bot_chat: bool
    ) -> User:
        return await cls.add(
            session,
            telegram_id=telegram_id,
            telegram_username=username,
            is_private=has_bot_chat
        )


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
        event_type
    ):
        new_event = cls.model(
            date_time=date_time,
            place=place,
            description=description,
            members_limit=members_limit,
            members_left=members_limit,
            event_type=event_type
        )
        db_session.add(new_event)
        await db_session.flush()
        return new_event


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
