from dataclasses import dataclass
from typing import Union

from aiogram import types
from aiogram.fsm.state import State

from src import messages
from src.models import Service
from src.stuff.appointments.keyboards import AppointmentDateTimePicker
from src.stuff.common.utils import dates_to_lang, form_services_list_text
from src.stuff.main_menu.keyboards import get_main_keyboard
from src.stuff.schedule.keyboards import Schedule


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


def get_logic_result(
    messages_to_answer: list[MessageToAnswer],
    state_to_set: State | None = None,
    data_to_set: dict | None = None,
    data_to_update: dict | None = None,
    clear_state: bool = False,
    messages_to_send: list[MessageToSend] | None = None,
) -> LogicResult:
    if messages_to_send is None:
        messages_to_send = []
    logic_result = LogicResult(
        messages_to_answer,
        state_to_set,
        data_to_set,
        data_to_update,
        clear_state,
        messages_to_send,
    )
    return logic_result


def to_main_menu_result(
    message_to_send: str = messages.MAIN_MENU,
    is_admin: bool = True,
) -> LogicResult:
    main_keyboard = get_main_keyboard(is_admin)
    messages_to_answer = [ MessageToAnswer(message_to_send, main_keyboard) ]
    return get_logic_result(messages_to_answer, clear_state=True)


def show_services(
    services: list[Service],
    keyboard: types.ReplyKeyboardMarkup,
    show_duration: bool,
) -> MessageToAnswer:
    text = form_services_list_text(services, show_duration)
    message_to_send = MessageToAnswer(text, keyboard)
    return message_to_send


def alert_not_available_to_choose_logic(
    callback_data: Union[AppointmentDateTimePicker, Schedule],
) -> str:
    alert_text = ""
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day
    if isinstance(callback_data, AppointmentDateTimePicker):
        week = None
        day_of_week = None
        for_what = "для записи"
    else:
        week = callback_data.week
        day_of_week = callback_data.day_of_week
        for_what = "для задания графика работы"
    lang_date = dates_to_lang(year, month, day, week, day_of_week)
    if week:
        alert_text = messages.WEEK_NOT_AVAILABLE.format(
            lang_week_month_year=lang_date,
            for_what=for_what,
        )
    elif day_of_week:
        alert_text = messages.DAY_OF_WEEK_NOT_AVAILABLE.format(
            lang_day_of_week_month_year=lang_date,
            for_what=for_what,
        )
    elif year and month and callback_data.day:
        alert_text = messages.DAY_NOT_AVAILABLE.format(
            lang_day_month_year=lang_date,
            for_what=for_what,
        )
    elif year and month:
        alert_text = messages.MONTH_NOT_AVAILABLE.format(
            lang_month_year=lang_date,
            for_what=for_what,
        )
    else:
        alert_text = messages.YEAR_NOT_AVAILABLE.format(
            lang_year=lang_date,
            for_what=for_what,
        )
    return alert_text
