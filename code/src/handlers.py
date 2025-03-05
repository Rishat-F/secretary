"""Обработчики бота."""

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import messages
from config import ADMIN_TG_ID
from database import get_uslugi
from keyboards import main_keyboard
from utils import form_uslugi_list_text


async def start_bot(message: types.Message):
    await message.answer(messages.GREETING, reply_markup=main_keyboard)


async def show_id(message: types.Message):
    await message.answer(
        messages.YOUR_ID.format(id=message.from_user.id), reply_markup=main_keyboard
    )


async def show_uslugi(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
):
    if message.from_user.id != ADMIN_TG_ID:
        uslugi = await get_uslugi(async_session)
        text = form_uslugi_list_text(uslugi)
        await message.answer(text, reply_markup=main_keyboard)
