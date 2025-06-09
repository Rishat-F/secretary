from dataclasses import dataclass

from aiogram import types
from aiogram.fsm.state import State


@dataclass
class MessageToAnswer:
    text: str
    keyboard: types.ReplyKeyboardMarkup | types.ReplyKeyboardRemove | types.InlineKeyboardMarkup


@dataclass
class MessageToSend:
    user_id: int
    text: str


@dataclass
class LogicResult:
    messages_to_answer: list[MessageToAnswer]
    state_to_set: State | None
    data_to_set: dict | None
    data_to_update: dict | None
    clear_state: bool
    messages_to_send: list[MessageToSend]
    edit_message: MessageToAnswer | None
    alert_text: str | None


def get_logic_result(
    messages_to_answer: list[MessageToAnswer] | None = None,
    state_to_set: State | None = None,
    data_to_set: dict | None = None,
    data_to_update: dict | None = None,
    clear_state: bool = False,
    messages_to_send: list[MessageToSend] | None = None,
    edit_message: MessageToAnswer | None = None,
    alert_text: str | None = None,
) -> LogicResult:
    if messages_to_answer is None:
        messages_to_answer = []
    if messages_to_send is None:
        messages_to_send = []
    logic_result = LogicResult(
        messages_to_answer,
        state_to_set,
        data_to_set,
        data_to_update,
        clear_state,
        messages_to_send,
        edit_message,
        alert_text,
    )
    return logic_result
