"""Работа с базой данных."""

from datetime import datetime

from sqlalchemy import and_, delete, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from src.models import Appointment, Reservation, Service, Slot
from src.utils import get_utc_now


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
        delete(Service)
        .where(and_(Service.name == name, Service.deleted.is_(False)))
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
        .where(Appointment.starts_at > get_utc_now())
        .order_by(Appointment.starts_at)
    )
    result = await session.execute(query)
    appointments = result.scalars().all()
    return list(appointments)


async def insert_appointment(session: AsyncSession, appointment: Appointment) -> None:
    session.add(appointment)


async def insert_slot(session: AsyncSession, slot: Slot) -> None:
    session.add(slot)


async def get_slots_by_date(session: AsyncSession, iso_date: str) -> list[Slot]:
    query = select(Slot).where(Slot.datetime_.istartswith(iso_date))
    result = await session.execute(query)
    slots = result.scalars().all()
    return list(slots)


async def delete_not_booked_future_slots(
    session: AsyncSession,
    current_utc_datetime: datetime,
) -> None:
    booked_slots = select(Reservation.datetime_).where(Reservation.datetime_ > current_utc_datetime)
    stmt = (
        delete(Slot)
        .where(and_(Slot.datetime_ > current_utc_datetime, Slot.datetime_.not_in(booked_slots)))
    )
    await session.execute(stmt)


async def delete_slots(
    session: AsyncSession,
    iso_utc_slots: list[str],
):
    for iso_utc_slot in iso_utc_slots:
        utc_datetime = datetime.fromisoformat(iso_utc_slot)
        stmt = delete(Slot).where(Slot.datetime_ == utc_datetime)
        try:
            await session.execute(stmt)
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def get_available_slots(
    session: AsyncSession,
    current_utc_datetime: datetime,
) -> list[Slot]:
    subquery = select(Reservation.datetime_)
    query = (
        select(Slot)
        .where(and_(Slot.datetime_ > current_utc_datetime, Slot.datetime_.not_in(subquery)))
        .order_by(Slot.datetime_)
    )
    result = await session.execute(query)
    slots = result.scalars().all()
    return list(slots)


async def get_future_slots(
    session: AsyncSession,
    current_utc_datetime: datetime,
) -> list[Slot]:
    query = (
        select(Slot)
        .where(Slot.datetime_ > current_utc_datetime)
        .order_by(Slot.datetime_)
    )
    result = await session.execute(query)
    slots = result.scalars().all()
    return list(slots)


async def insert_reservations(
    session: AsyncSession,
    datetimes_to_reserve: list[datetime],
    appointment_id: int,
) -> None:
    reservations = []
    for datetime_to_reserve in datetimes_to_reserve:
        reservations.append(
            Reservation(datetime_=datetime_to_reserve, appointment_id=appointment_id)
        )
    session.add_all(reservations)
