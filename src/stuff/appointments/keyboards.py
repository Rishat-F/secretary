from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.stuff.common.keyboards import (
    InlineButton,
    CANCEL,
    NO,
    YES,
    back_button,
)


ZAPIS_NA_PRIEM = "Записаться на прием"
SHOW_ACTIVE_ZAPISI = "Ваши записи"


class AppointmentDateTimePicker(CallbackData, prefix="appointment_pick_datetime", sep="$"):
    action: str
    year: int | None = None
    month: int | None = None
    day: int | None = None
    time: str | None = None


appointments_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [back_button],
        [
            KeyboardButton(text=ZAPIS_NA_PRIEM),
            KeyboardButton(text=SHOW_ACTIVE_ZAPISI),
        ],
    ],
    resize_keyboard=True,
)


def get_years_keyboard(years_keyboard_buttons: list[InlineButton]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in years_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=AppointmentDateTimePicker(action=button.action, year=int(button.value)),
        )
    builder.adjust(3)
    footer_builder = InlineKeyboardBuilder()
    footer_builder.button(
        text=CANCEL,
        callback_data=AppointmentDateTimePicker(action="cancel"),
    )
    builder.attach(footer_builder)
    return builder.as_markup()


def get_months_keyboard(
    chosen_year: int,
    months_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=str(chosen_year),
        callback_data=AppointmentDateTimePicker(action="choose_year"),
    )
    for button in months_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=AppointmentDateTimePicker(
                action=button.action,
                year=chosen_year,
                month=int(button.value),
            ),
        )
    builder.button(
        text=CANCEL,
        callback_data=AppointmentDateTimePicker(action="cancel"),
    )
    builder.adjust(1, 4, 4, 4, 1)
    return builder.as_markup()


def get_days_keyboard(
    chosen_year: int,
    chosen_month: int,
    days_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in days_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=AppointmentDateTimePicker(
                action=button.action,
                year=chosen_year,
                month=chosen_month,
                day=int(button.value),
            ),
        )
    builder.button(
        text=CANCEL,
        callback_data=AppointmentDateTimePicker(action="cancel"),
    )
    builder.adjust(2, 7, 7, 7, 7, 7, 7, 7, 7, 1)
    return builder.as_markup()


def get_times_keyboard(
    chosen_year: int,
    chosen_month: int,
    chosen_day: int,
    times_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in times_keyboard_buttons:
        if button.action == "confirm":
            time = button.value
        else:
            time = None
        builder.button(
            text=button.text,
            callback_data=AppointmentDateTimePicker(
                action=button.action,
                year=chosen_year,
                month=chosen_month,
                day=chosen_day,
                time=time,
            ),
        )
    builder.adjust(3, 6, 6, 6, 6, 6, 6, 6, 6)
    footer_builder = InlineKeyboardBuilder()
    footer_builder.button(
        text=CANCEL,
        callback_data=AppointmentDateTimePicker(action="cancel"),
    )
    builder.attach(footer_builder)
    return builder.as_markup()


def get_confirm_appointment_keyboard(chosen_datetime: datetime) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=YES,
        callback_data=AppointmentDateTimePicker(
            action="confirmed",
            year=chosen_datetime.year,
            month=chosen_datetime.month,
            day=chosen_datetime.day,
            time=chosen_datetime.time().isoformat(timespec="minutes"),
        ),
    )
    builder.button(
        text=NO, callback_data=AppointmentDateTimePicker(
            action="choose_time",
            year=chosen_datetime.year,
            month=chosen_datetime.month,
            day=chosen_datetime.day,
        ),
    )
    builder.button(text=CANCEL, callback_data=AppointmentDateTimePicker(action="cancel"))
    builder.adjust(1, 1, 1)
    return builder.as_markup()
