from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.stuff.appointments.logic import (
    appointment_confirmed_logic,
    cancel_choose_date_for_appointment_logic,
    choose_appointments_action_logic,
    choose_service_for_appointment_logic,
    go_to_choose_day_for_appointment_logic,
    go_to_choose_month_for_appointment_logic,
    go_to_choose_time_for_appointment_logic,
    go_to_choose_year_for_appointment_logic,
    go_to_confirm_appointment_logic,
)
from src.stuff.appointments.keyboards import AppointmentDateTimePicker
from src.stuff.common.handlers import process_logic_return


async def choose_appointments_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text or not message.from_user:
        return None
    async with async_session() as session:
        result = await choose_appointments_action_logic(
            message.text,
            message.from_user.id,
            session=session,
        )
    await process_logic_return(result, fsm_context=state, message=message)


async def choose_service_for_appointment(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await choose_service_for_appointment_logic(message.text, data, session)
    await process_logic_return(result, fsm_context=state, message=message)


async def go_to_choose_year_for_appointment(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_choose_year_for_appointment_logic(data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_choose_month_for_appointment(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_choose_month_for_appointment_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_choose_day_for_appointment(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_choose_day_for_appointment_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_choose_time_for_appointment(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_choose_time_for_appointment_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_confirm_appointment(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_confirm_appointment_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def appointment_confirmed(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
    bot: Bot,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = await appointment_confirmed_logic(callback, data, callback_data, async_session)
    await process_logic_return(result, fsm_context=state, callback=callback, bot=bot)


async def cancel_choose_date_for_appointment(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    result = cancel_choose_date_for_appointment_logic()
    await process_logic_return(result, fsm_context=state, callback=callback)
