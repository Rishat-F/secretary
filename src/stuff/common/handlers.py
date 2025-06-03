from typing import Any, Union

from aiogram import Bot, types
from aiogram.fsm.context import FSMContext

from src.stuff.appointments.keyboards import AppointmentDateTimePicker
from src.stuff.common.logic import LogicResult, alert_not_available_to_choose_logic
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
