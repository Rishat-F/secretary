from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.secrets import ADMIN_TG_ID
from src.stuff.common.handlers import process_logic_return
from src.stuff.main_menu.logic import (
    appointments_logic,
    schedule_logic,
    services_logic,
    start_bot_logic,
)


async def start_bot(message: types.Message, state: FSMContext) -> None:
    if message.from_user is None:
        return None
    is_admin = (message.from_user.id == ADMIN_TG_ID)
    result = start_bot_logic(is_admin)
    await process_logic_return(result, fsm_context=state, message=message)


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
