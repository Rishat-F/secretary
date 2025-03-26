"""ORM модели."""

from datetime import date
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, MetaData, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.constraints import USLUGA_NAME_MAX_LEN


constraint_naming_conventions = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


metadata = MetaData(naming_convention=constraint_naming_conventions)


class Base(DeclarativeBase):
    metadata = metadata


class Service(Base):
    __tablename__ = "service"
    __table_args__ = {"comment": "Услуга (например, 'Стрижка модельная')"}

    service_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
        comment="Идентификатор услуги",
    )
    name: Mapped[str] = mapped_column(
        String(USLUGA_NAME_MAX_LEN),
        nullable=False,
        unique=True,
        comment="Название услуги",
    )
    price: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Стоимость услуги",
    )
    duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Длительность предоставления услуги (в минутах, должно быть кратно 30)",
    )

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service")


class Appointment(Base):
    __tablename__ = "appointment"
    __table_args__ = {"comment": "Запись на прием"}

    appointment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
        comment="Идентификатор записи",
    )
    client_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Идентификатор клиента (телеграмм ID)",
    )
    service_id: Mapped[int | None] = mapped_column(
        ForeignKey("service.service_id", ondelete="SET NULL"),
        nullable=True,
        comment="Идентификатор услуги",
    )

    service: Mapped[Optional["Service"]] = relationship(back_populates="appointments", lazy="joined")
    slots: Mapped[list["Slot"]] = relationship(back_populates="appointment")


class Slot(Base):
    __tablename__ = "slot"
    __table_args__ = (
        UniqueConstraint("date_", "number"),
        {"comment": "Слоты приема (30 минутные интервалы)"},
    )

    slot_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
        comment="Идентификатор слота",
    )
    date_: Mapped[date] = mapped_column(Date, nullable=False, comment="Дата слота")
    number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment=(
            "Номер слота: "
            "1 - 00:00 - 00:30, "
            "2 - 00:30 - 01:00, "
            "..., "
            "47 - 23:00 - 23:30, "
            "48 - 23:00 - 00:00"
        ),
    )
    appointment_id: Mapped[int | None] = mapped_column(
        ForeignKey("appointment.appointment_id", ondelete="SET NULL"),
        nullable=True,
        comment="Идентификатор записи",
    )

    appointment: Mapped[Optional["Appointment"]] = relationship(back_populates="slots", lazy="joined")
