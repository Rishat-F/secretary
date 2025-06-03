from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.stuff.common.handlers import process_logic_return
from src.stuff.services.logic import (
    choose_service_field_to_update_logic,
    choose_service_to_delete_logic,
    choose_service_to_update_logic,
    choose_services_action_logic,
    set_service_duration_logic,
    set_service_name_logic,
    set_service_new_duration_logic,
    set_service_new_name_logic,
    set_service_new_price_logic,
    set_service_price_logic,
)


async def choose_services_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.text is None:
        return None
    async with async_session() as session:
        result = await choose_services_action_logic(message.text, session)
    await process_logic_return(result, fsm_context=state, message=message)


async def set_service_name(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.text is None:
        return None
    async with async_session() as session:
        result = await set_service_name_logic(message.text, session)
    await process_logic_return(result, fsm_context=state, message=message)


async def set_service_price(message: types.Message, state: FSMContext) -> None:
    if not message.text:
        return None
    result = await set_service_price_logic(message.text)
    await process_logic_return(result, fsm_context=state, message=message)


async def set_service_duration(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_service_duration_logic(message.text, session, data)
    await process_logic_return(result, fsm_context=state, message=message)


async def choose_service_to_delete(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    services_to_delete = await state.get_data()
    async with async_session() as session:
        result = await choose_service_to_delete_logic(message.text, session, services_to_delete)
    await process_logic_return(result, fsm_context=state, message=message)


async def choose_service_to_update(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    services_names = data["services_names"]
    async with async_session() as session:
        result = await choose_service_to_update_logic(message.text, session, services_names)
    await process_logic_return(result, fsm_context=state, message=message)


async def choose_service_field_to_update(
    message: types.Message,
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    services_names = data["services_names"]
    result = await choose_service_field_to_update_logic(message.text, services_names)
    await process_logic_return(result, fsm_context=state, message=message)


async def set_service_new_name(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_service_new_name_logic(message.text, session, data)
    await process_logic_return(result, fsm_context=state, message=message)


async def set_service_new_price(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_service_new_price_logic(message.text, session, data)
    await process_logic_return(result, fsm_context=state, message=message)


async def set_service_new_duration(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_service_new_duration_logic(message.text, session, data)
    await process_logic_return(result, fsm_context=state, message=message)
