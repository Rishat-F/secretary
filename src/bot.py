"""Телеграмм бот."""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.stuff.appointments.router import router as appointments_router
from src.stuff.common.router import router as common_router
from src.stuff.main_menu.router import router as main_menu_router
from src.stuff.schedule.router import router as schedule_router
from src.stuff.services.router import router as services_router
from src.config import db_url
from src.models import Base

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")


# https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#sqlite-foreign-keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, _):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


async def on_bot_start(engine: AsyncEngine) -> None:
    """Действия при запуске бота."""
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def main() -> None:
    """Запуск бота."""
    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(engine=engine, async_session=async_session)
    dp.startup.register(on_bot_start)
    dp.include_routers(
        appointments_router,
        main_menu_router,
        schedule_router,
        services_router,
        common_router,  # данный роутер должен подключаться последним!
    )
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
