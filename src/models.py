"""ORM модели."""

from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    false,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.constraints import DURATION_MULTIPLIER, MAX_DURATION, USLUGA_NAME_MAX_LEN


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
    __table_args__ = (
        CheckConstraint(
            f"(duration % {DURATION_MULTIPLIER}) == 0 and duration > 0 and duration < {MAX_DURATION}",
            name="duration_check"
        ),
        {"comment": "Услуга (например, 'Стрижка модельная')"},
    )

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
        comment="Длительность предоставления услуги (в минутах, должно быть кратно 30, больше 0 и меньше 1000)",
    )
    deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        comment="Удалена ли услуга",
        default=False,
        server_default=false(),
    )

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service")


class Appointment(Base):
    __tablename__ = "appointment"
    __table_args__ = (
        CheckConstraint("starts_at > CURRENT_TIMESTAMP", name="starts_at_gt_current_timestamp"),
        {"comment": "Прием (оказание услуги)"},
    )

    appointment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
        comment="Идентификатор приема (оказания услуги)",
    )
    client_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Идентификатор клиента (телеграмм ID)",
    )
    service_id: Mapped[int] = mapped_column(
        ForeignKey("service.service_id", ondelete="RESTRICT"),
        nullable=False,
        comment="Идентификатор услуги",
    )
    starts_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Дата и время начала приема (UTC, должно быть кратно 30 минутам)",
    )
    ends_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Дата и время окончания приема (UTC, должно быть кратно 30 минутам)",
    )

    service: Mapped["Service"] = relationship(back_populates="appointments", lazy="joined")


class Slot(Base):
    __tablename__ = "slot"
    __table_args__ = (
        CheckConstraint("datetime_ > CURRENT_TIMESTAMP", name="datetime__gt_current_timestamp"),
        {"comment": "Слоты приема (30 минутные интервалы)"},
    )

    datetime_: Mapped[datetime] = mapped_column(
        DateTime,
        primary_key=True,
        nullable=False,
        comment="Дата и время слота (UTC)",
    )


class Reservation(Base):
    __tablename__ = "reservation"
    __table_args__ = (
        CheckConstraint("datetime_ > CURRENT_TIMESTAMP", name="datetime__gt_current_timestamp"),
        {"comment": "Бронирование слотов (запись на прием)"},
    )

    datetime_: Mapped[datetime] = mapped_column(
        ForeignKey("slot.datetime_", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="Дата и время слота (UTC)",
    )
    appointment_id: Mapped[int] = mapped_column(
        ForeignKey("appointment.appointment_id", ondelete="CASCADE"),
        nullable=False,
        comment="Идентификатор приема (оказания услуги)",
    )
