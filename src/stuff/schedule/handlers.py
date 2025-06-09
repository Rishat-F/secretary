from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src import messages
from src.constraints import TG_ALERT_TEXT_MAX_LEN
from src.stuff.base.handlers import process_logic_return
from src.stuff.common.logic import to_main_menu_result
from src.stuff.schedule.keyboards import Schedule
from src.stuff.schedule.logic import (
    clear_schedule_clicked_logic,
    clear_schedule_confirmed_logic,
    day_clicked_logic,
    delete_schedule_logic,
    go_to_choose_day_while_view_schedule_logic,
    go_to_choose_month_for_set_schedule_logic,
    go_to_choose_month_while_view_schedule_logic,
    go_to_choose_year_for_set_schedule_logic,
    go_to_choose_year_while_view_schedule_logic,
    go_to_set_working_days_logic,
    go_to_set_working_hours_logic,
    save_schedule_logic,
    schedule_modifying_logic,
    show_working_hours_in_inline_mode_logic,
    show_working_hours_logic,
    time_clicked_logic,
)


async def go_to_main_menu(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    result = to_main_menu_result(messages.MAIN_MENU, is_admin=True)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def schedule_modifying(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    result = schedule_modifying_logic()
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_choose_year_for_set_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_choose_year_for_set_schedule_logic(data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_choose_month_for_set_schedule(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_choose_month_for_set_schedule_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_set_working_days(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_set_working_days_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_set_working_hours(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_set_working_hours_logic(data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def day_clicked(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: Schedule,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = day_clicked_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def time_clicked(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: Schedule,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = time_clicked_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def save_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = await save_schedule_logic(data, async_session)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def delete_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = await delete_schedule_logic(data, async_session)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def clear_schedule_clicked(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    result = clear_schedule_clicked_logic()
    await process_logic_return(result, fsm_context=state, callback=callback)


async def clear_schedule_confirmed(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    if not callback.message:
        return None
    result = await clear_schedule_confirmed_logic(async_session)
    await process_logic_return(result, fsm_context=state, callback=callback)
    await go_to_choose_day_while_view_schedule(callback, callback_data, state, async_session)


async def go_to_choose_year_while_view_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_choose_year_while_view_schedule_logic(data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_choose_month_while_view_schedule(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = go_to_choose_month_while_view_schedule_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def go_to_choose_day_while_view_schedule(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    if not callback.message:
        return None
    result = await go_to_choose_day_while_view_schedule_logic(callback_data, async_session)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def show_working_hours(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = show_working_hours_logic(data, callback_data)
    if result.alert_text and len(result.alert_text) > TG_ALERT_TEXT_MAX_LEN:
        await show_working_hours_in_inline_mode(callback, callback_data, state)
    else:
        await process_logic_return(result, fsm_context=state, callback=callback)


async def show_working_hours_in_inline_mode(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    result = show_working_hours_in_inline_mode_logic(data, callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)
