from typing import Any, Union

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from src import messages
from src.secrets import ADMIN_TG_ID
from src.stuff.appointments.keyboards import AppointmentDateTimePicker
from src.stuff.common.logic import (
    LogicResult,
    alert_not_available_to_choose_logic,
    to_main_menu_result,
)
from src.stuff.main_menu.keyboards import get_main_keyboard
from src.stuff.schedule.keyboards import Schedule


async def process_logic_return(
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


async def alert_not_available_to_choose(
    callback: types.CallbackQuery,
    callback_data: Union[AppointmentDateTimePicker, Schedule],
) -> None:
    alert_text = alert_not_available_to_choose_logic(callback_data)
    await callback.answer(alert_text, show_alert=True)


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
    for_admin = (callback.from_user.id == ADMIN_TG_ID)
    main_keyboard = get_main_keyboard(for_admin=for_admin)
    try:
        await callback.message.delete()
    except TelegramBadRequest:  # давние сообщения удалять нельзя
        pass
    await callback.message.answer(
        text=messages.SOMETHING_GONE_WRONG_TRY_FROM_BEGINNING,
        reply_markup=main_keyboard,
    )
    await state.clear()
    await callback.answer()
