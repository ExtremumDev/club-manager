from aiogram import types

from .base_paging import Paging

from utils.enums import EventType

from markups.admin.event_manage import get_events_list_markup

from database.dao import MembersEventDAO
from database.utils import connection


class EventsPaging(Paging):

    def __init__(self, page: int = 0):
        super().__init__(page, "events")

    async def get_queryset(
        self, db_session: AsyncSession, event_type: EventType, *args, **kwargs
    ):
        self.queryset = await MembersEventDAO.get_all_events_by_type(
            db_session=db_session,
            event_type=event_type
        )


    def get_reply_markup(
        self,
        reply_markup: types.InlineKeyboardMarkup = None,
        extra_data: str ='',
        *args, **kwargs
    ):
        return super().get_reply_markup(
            reply_markup=get_events_list_markup(
                events=self.queryset
            ),
            extra_data=extra_data
        )


    @classmethod
    @connection
    async def next_page_handler(
        cls, c: types.CallbackQuery, db_session, *args
    ):
        a, page, event_type = c.data.split('_')

        paging = cls(int(page))
        await paging.get_queryset(db_session, event_type)
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

        paging = cls(int(page))
        await paging.get_queryset(db_session, event_type)
        await paging.create_prev_page()

        await c.message.edit_reply_markup(
            reply_markup=paging.get_reply_markup(
                extra_data=f"_{event_type}"
            )
        )

        await c.answer()


    @classmethod
    def register_paging_handlers(cls, dp):
        super().register_paging_handlers(dp, prefix="events")
