"""Обработчики бота."""

from typing import Any

from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.handlers.logic import (
    LogicResult,
    choose_day_to_zapis_logic,
    choose_month_to_zapis_logic,
    choose_time_to_zapis_logic,
    choose_usluga_field_to_update_logic,
    choose_usluga_to_delete_logic,
    choose_usluga_to_update_logic,
    choose_usluga_to_zapis_logic,
    choose_uslugi_action_logic,
    choose_year_to_zapis_logic,
    choose_zapisi_action_logic,
    set_usluga_duration_logic,
    set_usluga_name_logic,
    set_usluga_new_duration_logic,
    set_usluga_new_name_logic,
    set_usluga_new_price_logic,
    set_usluga_price_logic,
    uslugi_logic,
    zapisi_logic,
)
from src import messages
from src.keyboards import main_keyboard


async def _process_logic_return(
    logic_result: LogicResult,
    fsm_context: FSMContext,
    message: types.Message,
    bot: Bot | None = None,
) -> Any:
    if logic_result.clear_state:
        await fsm_context.clear()
    else:
        if logic_result.state_to_set:
            await fsm_context.set_state(logic_result.state_to_set)
        if isinstance(logic_result.data_to_set, dict):
            await fsm_context.set_data(logic_result.data_to_set)
        if isinstance(logic_result.data_to_update, dict):
            await fsm_context.update_data(logic_result.data_to_update)
    for message_to_answer in logic_result.messages_to_answer:
        await message.answer(
            message_to_answer.text,
            reply_markup=message_to_answer.keyboard,
        )
    if bot:
        for message_to_send in logic_result.messages_to_send:
            await bot.send_message(message_to_send.user_id, message_to_send.text)


async def start_bot(message: types.Message):
    await message.answer(messages.GREETING, reply_markup=main_keyboard)


async def uslugi(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    async with async_session() as session:
        result = await uslugi_logic(user_id=message.from_user.id, session=session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_uslugi_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.text is None:
        return None
    async with async_session() as session:
        result = await choose_uslugi_action_logic(message.text, session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_usluga_name(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.text is None:
        return None
    async with async_session() as session:
        result = await set_usluga_name_logic(message.text, session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_usluga_price(message: types.Message, state: FSMContext) -> None:
    if not message.text:
        return None
    result = await set_usluga_price_logic(message.text)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_usluga_duration(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_usluga_duration_logic(message.text, session, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_usluga_to_delete(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    uslugi_to_delete = await state.get_data()
    async with async_session() as session:
        result = await choose_usluga_to_delete_logic(message.text, session, uslugi_to_delete)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_usluga_to_update(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    uslugi_names = data["uslugi_names"]
    async with async_session() as session:
        result = await choose_usluga_to_update_logic(message.text, session, uslugi_names)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_usluga_field_to_update(
    message: types.Message,
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    uslugi_names = data["uslugi_names"]
    result = await choose_usluga_field_to_update_logic(message.text, uslugi_names)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_usluga_new_name(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_usluga_new_name_logic(message.text, session, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_usluga_new_price(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_usluga_new_price_logic(message.text, session, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_usluga_new_duration(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_usluga_new_duration_logic(message.text, session, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def zapisi(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    async with async_session() as session:
        result = await zapisi_logic(user_id=message.from_user.id, session=session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_zapisi_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text or not message.from_user:
        return None
    async with async_session() as session:
        result = await choose_zapisi_action_logic(
            message.text,
            message.from_user.id,
            session=session,
        )
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_usluga_to_zapis(message: types.Message, state: FSMContext) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    result = await choose_usluga_to_zapis_logic(message.text, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_year_to_zapis(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await choose_year_to_zapis_logic(message.text, data, session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_month_to_zapis(message: types.Message, state: FSMContext) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    result = await choose_month_to_zapis_logic(message.text, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_day_to_zapis(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await choose_day_to_zapis_logic(message.text, data, session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_time_to_zapis(
    message: types.Message,
    bot: Bot,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text or not message.from_user:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await choose_time_to_zapis_logic(
            message.text,
            message.from_user.id,
            data,
            session,
        )
    await _process_logic_return(result, fsm_context=state, message=message, bot=bot)
