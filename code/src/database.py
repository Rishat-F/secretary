"""Работа с базой данных."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


from models import Usluga


async def get_uslugi(
    async_session: async_sessionmaker[AsyncSession],
    filter_by: dict | None = None,
) -> list[Usluga]:
    if filter_by is None:
        filter_by = dict()
    async with async_session() as session:
        query = select(Usluga).filter_by(**filter_by)
        result = await session.execute(query)
        uslugi = result.scalars().all()
    return list(uslugi)


async def insert_usluga(
    async_session: async_sessionmaker[AsyncSession],
    usluga: Usluga,
) -> None:
    async with async_session() as session:
        session.add(usluga)
        await session.commit()
