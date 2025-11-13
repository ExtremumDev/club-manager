from sqlalchemy.ext.asyncio import AsyncSession

from .base_paging import Paging


class DatingPaging(Paging):

    def get_queryset(self, db_session: AsyncSession, *args, **kwargs):

