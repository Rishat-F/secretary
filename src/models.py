"""ORM модели."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from src.constraints import USLUGA_NAME_MAX_LEN


constraint_naming_conventions = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


metadata = MetaData(naming_convention=constraint_naming_conventions)


class Base(DeclarativeBase):
    metadata = metadata


class Usluga(Base):
    __tablename__ = "usluga"
    __table_args__ = {"comment": "Услуга (например, 'Стрижка модельная')"}

    usluga_id: Mapped[int] = mapped_column(
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

    zapisi: Mapped[list["Zapis"]] = relationship(back_populates="usluga")


class Zapis(Base):
    __tablename__ = "zapis"
    __table_args__ = {"comment": "Запись на прием"}

    zapis_id: Mapped[int] = mapped_column(
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
    usluga_id: Mapped[int | None] = mapped_column(
        ForeignKey("usluga.usluga_id", ondelete="SET NULL"),
        nullable=True,
        comment="Идентификатор услуги",
    )
    starts_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Дата и время начала приема (должно быть кратно 30 минутам)",
    )
    ends_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Дата и время окончания приема (должно быть кратно 30 минутам)",
    )

    usluga: Mapped[Optional["Usluga"]] = relationship(back_populates="zapisi", lazy="joined")
