from sqlalchemy.ext.asyncio import AsyncSession


from aiogram import types


from .events_paging import EventsPaging

from markups.admin.event_manage import get_events_list_markup

from database.dao import MembersEventDAO
from database.utils import connection

from utils.enums import EventType


class UserEventsPaging(EventsPaging):
    def __init__(self, event_type: EventType, page: int = 0):
        super().__init__(event_type, page)
        self.prefix = 'u'

    async def get_queryset(
        self, db_session: AsyncSession, user_id,
        *args, **kwargs
    ):

        self.queryset = await MembersEventDAO.get_all_events_by_type_and_user(
            db_session=db_session,
            event_type=self.event_type,
            user_id=user_id
        )


    @classmethod
    @connection
    async def next_page_handler(
        cls, c: types.CallbackQuery, db_session, *args
    ):
        a, page, event_type = c.data.split('_')

        paging = cls(EventType(int(event_type)), int(page))
        await paging.get_queryset(
            db_session,
            user_id=c.from_user.id
        )
        await paging.create_next_page()

        await c.message.edit_reply_markup(
            reply_markup=paging.get_reply_markup(
                extra_data=f"_{event_type}"
            )
        )

        await c.answer()

    @classmethod
    @connection
    async def prev_page_handler(cls, c: types.CallbackQuery, db_session, *args):
        a, page, event_type = c.data.split('_')

        paging = cls(EventType(int(event_type)), int(page))
        await paging.get_queryset(
            db_session,
            c.from_user.id
        )

        await paging.create_prev_page()

        await c.message.edit_reply_markup(
            reply_markup=paging.get_reply_markup(
                extra_data=f"_{event_type}"
            )
        )

        await c.answer()

    @classmethod
    def register_paging_handlers(cls, dp):
        super().register_paging_handlers(dp, prefix='u')
