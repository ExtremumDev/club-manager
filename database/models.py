from sqlalchemy.orm import (
    DeclarativeBase, declared_attr, Mapped, mapped_column, relationship
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import BigInteger, func, String, Boolean, ForeignKey

from typing import List

import datetime

from utils.enums import EventType, Sex


class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        table_name = []
        table_name.append(cls.__name__[0].lower())
        for c in cls.__name__[1:]:
            if c.isupper():
                table_name.append('_')
                table_name.append(c.lower())
            else:
                table_name.append(c)

        return ''.join(table_name) + 's'

    def model_to_dict(model_instance):
        return {column.name: getattr(model_instance, column.name) 
                for column in model_instance.__table__.columns}



class User(Base):
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    telegram_username: Mapped[str] = mapped_column(String(32))

    register_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    
    has_private: Mapped[bool] = mapped_column()
    is_admin: Mapped[bool] = mapped_column(default=False)

    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user")
    profile_id: Mapped[int] = mapped_column(ForeignKey("user_profiles.id"), nullable=True)

    memberships: Mapped[List["EventMembership"]] = relationship(
        "EventMembership",
        back_populates="user"
    )

    initiatives: Mapped[List["Initiative"]] = relationship(
        "Initiative",
        back_populates="creator"
    )


class UserProfile(Base):
    user: Mapped["User"] = relationship(
        "User",
        back_populates="profile"
    )

    name: Mapped[str] = mapped_column(String(100), server_default="Не указано")
    alias: Mapped[str] = mapped_column(String(100), server_default="Анонимный пользователь")
    city: Mapped[str] = mapped_column(String(20))
    birthday: Mapped[datetime.datetime] = mapped_column()
    interests: Mapped[str] = mapped_column(String(150))
    sex: Mapped[Sex] = mapped_column(nullable=True)
    social_link: Mapped[str] = mapped_column(String(100), nullable=True)

    rating: Mapped[int] = mapped_column(default=0)


class Initiative(Base):

    creator: Mapped["User"] = relationship(
        "User",
        back_populates="initiatives",
        lazy="joined"
    )
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    date_time: Mapped[datetime.datetime] = mapped_column()
    place: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(300))
    activity_type: Mapped[str] = mapped_column(String(50), nullable=True)
    verified: Mapped[bool] = mapped_column(default=False)


class MemberEvent(Base):
    date_time: Mapped[datetime.datetime] = mapped_column()
    place: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(200))
    members_limit: Mapped[int] = mapped_column(default=1)
    members_left: Mapped[int] = mapped_column(default=0)
    activity_name: Mapped[str] = mapped_column(String(100), nullable=True)
    event_type: Mapped[EventType] = mapped_column()
    holder: Mapped[str] = mapped_column(String(100), server_default="Не указан")

    info_message_id: Mapped[int] = mapped_column(BigInteger, server_default="0")

    members: Mapped[List["EventMembership"]] = relationship(
        "EventMembership",
        back_populates="event",
        cascade="all, delete-orphan",  # ← ключевой параметр
        passive_deletes=True
    )


class EventMembership(Base):

    user: Mapped["User"] = relationship(
        "User",
        back_populates="memberships"
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    event: Mapped["MemberEvent"] = relationship(
        "MemberEvent",
        back_populates="members"
    )
    event_id: Mapped[int] = mapped_column(ForeignKey("member_events.id", ondelete="CASCADE"))

    created_ad: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    is_member: Mapped[bool] = mapped_column(default=True)
    is_come: Mapped[bool] = mapped_column(default=False)
    name: Mapped[str] = mapped_column(nullable=True)
    is_bot_user: Mapped[bool] = mapped_column(default=True)


class DatingProfile(Base):

    user: Mapped["User"] = relationship(
        "User",
        back_populates="dating_profiles"
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    photo: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(String(300))
    interests: Mapped[str] = mapped_column(String(300))
    goal: Mapped[str] = mapped_column(String(20))

