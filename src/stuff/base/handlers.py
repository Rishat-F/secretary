from typing import Any

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext

from src.stuff.base.logic import LogicResult


async def process_logic_return(
    logic_result: LogicResult,
    fsm_context: FSMContext,
    message: types.Message | None = None,
    callback: types.CallbackQuery | None = None,
    bot: Bot | None = None,
) -> Any:
    if message:
        assert not callback
    else:
        assert callback
    if logic_result.messages_to_send:
        assert bot
    if logic_result.clear_state:
        await fsm_context.clear()
    else:
        if logic_result.state_to_set:
            await fsm_context.set_state(logic_result.state_to_set)
        if isinstance(logic_result.data_to_set, dict):
            await fsm_context.set_data(logic_result.data_to_set)
        if isinstance(logic_result.data_to_update, dict):
            await fsm_context.update_data(logic_result.data_to_update)
    if message:
        for message_to_answer in logic_result.messages_to_answer:
            await message.answer(
                message_to_answer.text,
                reply_markup=message_to_answer.keyboard,
            )
    elif callback:
        if not callback.message:
            return None
        if logic_result.edit_message:
            assert isinstance(logic_result.edit_message.keyboard, types.InlineKeyboardMarkup)
            await callback.message.edit_text(
                text=logic_result.edit_message.text,
                reply_markup=logic_result.edit_message.keyboard,
            )
        if logic_result.messages_to_answer:
            try:
                await callback.message.delete()
            except TelegramBadRequest:  # давние сообщения удалять нельзя
                pass
            for message_to_answer in logic_result.messages_to_answer:
                await callback.message.answer(
                    message_to_answer.text,
                    reply_markup=message_to_answer.keyboard,
                )
        if logic_result.alert_text:
            await callback.answer(logic_result.alert_text, show_alert=True)
        else:
            await callback.answer()
    if bot:
        for message_to_send in logic_result.messages_to_send:
            await bot.send_message(message_to_send.user_id, message_to_send.text)
