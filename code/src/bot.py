"""Телеграмм бот."""

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ChatType, ParseMode
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from config import db_url
from handlers import show_id, show_uslugi, start_bot
from keyboards import SHOW_ID, USLUGI
from models import Base

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков."""
    dp.message.register(
        start_bot,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower().contains("/start"),
    )
    dp.message.register(
        show_id,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower() == SHOW_ID.lower(),
    )
    dp.message.register(
        show_uslugi,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower() == USLUGI.lower(),
    )


async def on_bot_start(engine: AsyncEngine) -> None:
    """Действия при запуске бота."""
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def main() -> None:
    """Запуск бота."""
    engine = create_async_engine(db_url, echo=True)
    async_session = async_sessionmaker(engine)
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.startup.register(on_bot_start)
    register_handlers(dp)
    await bot.delete_webhook(drop_pending_updates=True)
    dp["engine"] = engine
    dp["async_session"] = async_session
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
