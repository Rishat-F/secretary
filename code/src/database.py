"""Работа с базой данных."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


from models import Usluga


async def get_uslugi(
    async_session: async_sessionmaker[AsyncSession],
) -> list[Usluga]:
    async with async_session() as session:
        query = select(Usluga)
        result = await session.execute(query)
        uslugi = result.scalars().all()
    return list(uslugi)
