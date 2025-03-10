"""Работа с базой данных."""

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


from models import Usluga


async def get_uslugi(
    async_session: async_sessionmaker[AsyncSession],
    filter_by: dict | None = None,
) -> list[Usluga]:
    if filter_by is None:
        filter_by = dict()
    async with async_session() as session:
        query = select(Usluga).filter_by(**filter_by).order_by(Usluga.name)
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


async def update_usluga(
    async_session: async_sessionmaker[AsyncSession],
    usluga_name: str,
    new_values: dict,
) -> None:
    async with async_session() as session:
        stmt = update(Usluga).where(Usluga.name == usluga_name).values(**new_values)
        await session.execute(stmt)
        await session.commit()


async def delete_usluga(
    async_session: async_sessionmaker[AsyncSession],
    name: str,
) -> None:
    async with async_session() as session:
        query = delete(Usluga).where(Usluga.name==name)
        await session.execute(query)
        await session.commit()
