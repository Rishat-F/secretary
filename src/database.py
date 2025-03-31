"""Работа с базой данных."""

from datetime import datetime

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession


from src.models import Service, Appointment


async def get_services(
    session: AsyncSession,
    filter_by: dict | None = None,
) -> list[Service]:
    if filter_by is None:
        filter_by = dict()
    query = (
        select(Service)
        .filter_by(**filter_by)
        .where(Service.deleted.is_(False))
        .order_by(Service.name)
    )
    result = await session.execute(query)
    services = result.scalars().all()
    return list(services)


async def insert_service(session: AsyncSession, service: Service) -> None:
    session.add(service)
    await session.commit()


async def update_service(
    session: AsyncSession,
    service_name: str,
    new_values: dict,
) -> None:
    stmt = (
        update(Service)
        .where(and_(Service.name == service_name, Service.deleted.is_(False)))
        .values(**new_values)
    )
    await session.execute(stmt)
    await session.commit()


async def delete_service(session: AsyncSession, name: str) -> None:
    stmt = (
        update(Service)
        .where(and_(Service.name == name, Service.deleted.is_(False)))
        .values(deleted=True)
    )
    await session.execute(stmt)
    await session.commit()


async def get_active_appointments(
    session: AsyncSession,
    filter_by: dict | None = None,
) -> list[Appointment]:
    if filter_by is None:
        filter_by = dict()
    query = (
        select(Appointment)
        .filter_by(**filter_by)
        .where(Appointment.starts_at > datetime.now())
        .order_by(Appointment.starts_at)
    )
    result = await session.execute(query)
    appointments = result.scalars().all()
    return list(appointments)


async def insert_appointment(session: AsyncSession, appointment: Appointment) -> None:
    session.add(appointment)
    await session.commit()
