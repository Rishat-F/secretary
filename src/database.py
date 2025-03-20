"""Работа с базой данных."""

from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession


from src.models import Usluga, Zapis


async def get_uslugi(
    session: AsyncSession,
    filter_by: dict | None = None,
) -> list[Usluga]:
    if filter_by is None:
        filter_by = dict()
    query = select(Usluga).filter_by(**filter_by).order_by(Usluga.name)
    result = await session.execute(query)
    uslugi = result.scalars().all()
    return list(uslugi)


async def insert_usluga(session: AsyncSession, usluga: Usluga) -> None:
    session.add(usluga)
    await session.commit()


async def update_usluga(
    session: AsyncSession,
    usluga_name: str,
    new_values: dict,
) -> None:
    stmt = update(Usluga).where(Usluga.name == usluga_name).values(**new_values)
    await session.execute(stmt)
    await session.commit()


async def delete_usluga(session: AsyncSession, name: str) -> None:
    query = delete(Usluga).where(Usluga.name==name)
    await session.execute(query)
    await session.commit()


async def get_active_zapisi(
    session: AsyncSession,
    filter_by: dict | None = None,
) -> list[Zapis]:
    if filter_by is None:
        filter_by = dict()
    query = (
        select(Zapis)
        .filter_by(**filter_by)
        .where(Zapis.starts_at > datetime.now())
        .order_by(Zapis.starts_at)
    )
    result = await session.execute(query)
    zapisi = result.scalars().all()
    return list(zapisi)


async def insert_zapis(session: AsyncSession, zapis: Zapis) -> None:
    session.add(zapis)
    await session.commit()
