from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src import messages
from src.secrets import ADMIN_TG_ID
from src.stuff.common.handlers import process_logic_return
from src.stuff.main_menu.keyboards import get_main_keyboard
from src.stuff.main_menu.logic import (
    schedule_logic,
    services_logic,
    appointments_logic,
)


async def start_bot(message: types.Message):
    if message.from_user is None:
        return None
    if message.from_user.id == ADMIN_TG_ID:
        main_keyboard = get_main_keyboard(for_admin=True)
    else:
        main_keyboard = get_main_keyboard(for_admin=False)
    await message.answer(messages.GREETING, reply_markup=main_keyboard)


async def services(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    async with async_session() as session:
        result = await services_logic(user_id=message.from_user.id, session=session)
    await process_logic_return(result, fsm_context=state, message=message)


async def appointments(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    async with async_session() as session:
        result = await appointments_logic(user_id=message.from_user.id, session=session)
    await process_logic_return(result, fsm_context=state, message=message)


async def schedule(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    async with async_session() as session:
        result = await schedule_logic(session)
    await process_logic_return(result, fsm_context=state, message=message)
