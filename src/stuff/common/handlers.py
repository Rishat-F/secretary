from typing import Union

from aiogram import types
from aiogram.fsm.context import FSMContext

from src import messages
from src.secrets import ADMIN_TG_ID
from src.stuff.appointments.keyboards import AppointmentDateTimePicker
from src.stuff.base.handlers import process_logic_return
from src.stuff.common.logic import (
    alert_not_available_to_choose_logic,
    to_main_menu_result,
)
from src.stuff.schedule.keyboards import Schedule


async def alert_not_available_to_choose(
    callback: types.CallbackQuery,
    callback_data: Union[AppointmentDateTimePicker, Schedule],
    state: FSMContext,
) -> None:
    result = alert_not_available_to_choose_logic(callback_data)
    await process_logic_return(result, fsm_context=state, callback=callback)


async def ignore_inline_button(callback: types.CallbackQuery) -> None:
    await callback.answer()


async def emergency_returning_to_main_menu_from_reply_mode(
    message: types.Message,
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    is_admin = (message.from_user.id == ADMIN_TG_ID)
    result = to_main_menu_result(
        messages.SOMETHING_GONE_WRONG_TRY_FROM_BEGINNING,
        is_admin=is_admin,
    )
    await process_logic_return(result, fsm_context=state, message=message)


async def emergency_returning_to_main_menu_from_inline_mode(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    is_admin = (callback.from_user.id == ADMIN_TG_ID)
    result = to_main_menu_result(
        messages.SOMETHING_GONE_WRONG_TRY_FROM_BEGINNING,
        is_admin=is_admin,
    )
    await process_logic_return(result, fsm_context=state, callback=callback)
