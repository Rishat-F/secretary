"""Обработчики бота."""

from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

import messages
from config import ADMIN_TG_ID
from database import get_uslugi
from keyboards import BACK, SHOW_ALL_USLUGI, main_keyboard, uslugi_keyboard
from states import UslugiActions
from utils import form_uslugi_list_text


async def start_bot(message: types.Message):
    await message.answer(messages.GREETING, reply_markup=main_keyboard)


async def show_id(message: types.Message):
    await message.answer(
        messages.YOUR_ID.format(id=message.from_user.id), reply_markup=main_keyboard
    )


async def _show_uslugi(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    keyboard: types.ReplyKeyboardMarkup,
) -> None:
    uslugi = await get_uslugi(async_session)
    text = form_uslugi_list_text(uslugi)
    await message.answer(text, reply_markup=keyboard)


async def uslugi(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
):
    if message.from_user.id != ADMIN_TG_ID:
        await _show_uslugi(message, async_session, main_keyboard)
    else:
        await message.answer(messages.CHOOSE_ACTION, reply_markup=uslugi_keyboard)
        await state.set_state(UslugiActions.choose_action)


async def choose_uslugi_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    upper_text = message.text.upper()
    if upper_text == BACK.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=main_keyboard)
    elif upper_text == SHOW_ALL_USLUGI.upper():
        await _show_uslugi(message, async_session, uslugi_keyboard)
    else:
        await message.answer(messages.CHOOSE_GIVEN_ACTION, reply_markup=uslugi_keyboard)
