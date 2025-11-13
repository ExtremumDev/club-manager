from sys import prefix

from aiogram import types


from sqlalchemy.ext.asyncio import AsyncSession

from .base_paging import Paging

from utils.enums import EventType

from markups.admin.event_manage import get_events_list_markup

from database.dao import MembersEventDAO
from database.utils import connection


class EventsPaging(Paging):
    EMPTY_SET_MESSAGE = "Не найдено мероприятий"

    def __init__(self, event_type: EventType, page: int = 0, prefix: str = ''):
        super().__init__(page)
        self.event_type = event_type
        self.prefix = prefix

    async def get_queryset(
        self, db_session: AsyncSession, *args, **kwargs
    ):
        self.queryset = await MembersEventDAO.get_all_events_by_type(
            db_session=db_session,
            event_type=self.event_type
        )


    def get_reply_markup(
        self,
        reply_markup: types.InlineKeyboardMarkup = None,
        extra_data: str ='',
        *args, **kwargs
    ):
        return super().get_reply_markup(
            reply_markup=get_events_list_markup(
                events=self.queryset,
                prefix=self.prefix
            ),
            extra_data=f"_{self.event_type.value}"
        )


    @classmethod
    @connection
    async def next_page_handler(
        cls, c: types.CallbackQuery, db_session, *args
    ):
        a, page, event_type = c.data.split('_')

        if c.data.startswith("af"):
            paging_prefix = "af"
        else:
            paging_prefix = ""

        paging = cls(event_type=EventType(int(event_type)), page=int(page), prefix=paging_prefix)
        await paging.get_queryset(db_session)
        await paging.create_next_page()

        await c.message.edit_reply_markup(
            reply_markup=paging.get_reply_markup()
        )

        await c.answer()

    @classmethod
    @connection
    async def prev_page_handler(cls, c: types.CallbackQuery, db_session, *args):
        a, page, event_type = c.data.split('_')

        if c.data.startswith("af"):
            paging_prefix = "af"
        else:
            paging_prefix = ""

        paging = cls(event_type=EventType(int(event_type)), page=int(page), prefix=paging_prefix)
        await paging.get_queryset(db_session)
        await paging.create_prev_page()

        await c.message.edit_reply_markup(
            reply_markup=paging.get_reply_markup()
        )

        await c.answer()


    @classmethod
    def register_paging_handlers(cls, dp, data_prefix=''):
        super().register_paging_handlers(dp, prefix=data_prefix + "events")
