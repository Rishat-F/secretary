"""Клавиатуры бота."""

from datetime import datetime
from typing import NamedTuple

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.utils import months

BACK = "Назад"
MAIN_MENU = "Главная"
USLUGI = "Услуги"
CREATE = "Создать"
UPDATE = "Изменить"
DELETE = "Удалить"
SHOW_ALL_USLUGI = "Показать все услуги"
NAME = "Название"
PRICE = "Стоимость"
DURATION = "Длительность"
UPDATE_ANOTHER_USLUGA = "Изменить другую услугу"
ZAPISI = "Записи"
ZAPIS_NA_PRIEM = "Записаться на прием"
SHOW_ACTIVE_ZAPISI = "Ваши записи"
CANCEL = "Отмена"
YES = "Да"
NO = "Нет"
SCHEDULE = "График работы"
CLEAR = "Обнулить"
MODIFY = "Изменить"
SAVE = "Сохранить"
DELETE = "Удалить"
SET_TIME = "Задать время"
SET_DATE = "Задать даты"
VIEW = "Просмотр"

back_button = KeyboardButton(text=BACK)
main_menu_button = KeyboardButton(text=MAIN_MENU)


class InlineButton(NamedTuple):
    action: str
    text: str
    value: str


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=USLUGI), KeyboardButton(text=ZAPISI)],
        [KeyboardButton(text=SCHEDULE)],
    ],
    resize_keyboard=True,
)

services_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [back_button, KeyboardButton(text=SHOW_ALL_USLUGI)],
        [
            KeyboardButton(text=CREATE),
            KeyboardButton(text=UPDATE),
            KeyboardButton(text=DELETE),
        ],
    ],
    resize_keyboard=True,
)

back_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [back_button, main_menu_button],
    ],
    resize_keyboard=True,
)


def _arrange_buttons(
    texts: list[str],
    buttons_in_row: int,
) -> list[list[KeyboardButton]]:
    arranged_buttons = []
    row = []
    for text in texts:
        row.append(KeyboardButton(text=text))
        if len(row) == buttons_in_row:
            arranged_buttons.append(row)
            row = []
    if row:
        arranged_buttons.append(row)
    return arranged_buttons


def get_services_to_update_keyboard(names: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [
        [back_button, main_menu_button],
    ]
    arranged_services_names_buttons = _arrange_buttons(names, buttons_in_row=2)
    keyboard.extend(arranged_services_names_buttons)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


service_fields_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [back_button, main_menu_button],
        [
            KeyboardButton(text=NAME),
            KeyboardButton(text=PRICE),
            KeyboardButton(text=DURATION),
        ],
    ],
    resize_keyboard=True,
)

set_service_new_field_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [back_button, main_menu_button],
        [
            KeyboardButton(text=UPDATE_ANOTHER_USLUGA),
        ],
    ],
    resize_keyboard=True,
)


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


class AppointmentDateTimePicker(CallbackData, prefix="appointment_pick_datetime", sep="$"):
    action: str
    year: int | None = None
    month: int | None = None
    day: int | None = None
    time: str | None = None


class Schedule(CallbackData, prefix="schedule", sep="$"):
    action: str
    year: int | None = None
    month: int | None = None
    day: int | None = None
    time: str | None = None
    index: int | None = None


def make_appointment_get_years_keyboard(years_keyboard_buttons: list[InlineButton]) -> InlineKeyboardMarkup:
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


def make_appointment_get_months_keyboard(
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


def make_appointment_get_days_keyboard(
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


def make_appointment_get_times_keyboard(
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


def _attach_edit_schedule_buttons(builder: InlineKeyboardBuilder) -> None:
    builder_to_attach = InlineKeyboardBuilder()
    builder_to_attach.button(
        text=MODIFY,
        callback_data=Schedule(action="modify_schedule"),
    )
    builder_to_attach.button(
        text=CLEAR,
        callback_data=Schedule(action="clear_schedule"),
    )
    builder_to_attach.adjust(1, 1)
    builder.attach(builder_to_attach)


def _attach_modify_buttons_for_edit_schedule(builder: InlineKeyboardBuilder) -> None:
    builder_to_attach = InlineKeyboardBuilder()
    builder_to_attach.button(
        text=SAVE,
        callback_data=Schedule(action="save"),
    )
    builder_to_attach.button(
        text=DELETE,
        callback_data=Schedule(action="delete"),
    )
    builder.attach(builder_to_attach)


def _attach_footer_buttons_for_schedule(
    builder: InlineKeyboardBuilder,
    with_view_button: bool,
) -> None:
    builder_to_attach = InlineKeyboardBuilder()
    if with_view_button:
        builder_to_attach.button(
            text=VIEW,
            callback_data=Schedule(action="view_schedule"),
        )
    builder_to_attach.button(
        text=MAIN_MENU,
        callback_data=Schedule(action="main_menu"),
    )
    builder.attach(builder_to_attach)


def set_schedule_get_years_keyboard(years_keyboard_buttons: list[InlineButton]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in years_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=Schedule(action=button.action, year=int(button.value)),
        )
    builder.button(
        text=SET_TIME,
        callback_data=Schedule(action="set_time"),
    )
    builder.adjust(2, 1)
    _attach_modify_buttons_for_edit_schedule(builder)
    _attach_footer_buttons_for_schedule(builder, with_view_button=True)
    return builder.as_markup()


def set_schedule_get_months_keyboard(
    chosen_year: int,
    months_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=str(chosen_year),
        callback_data=Schedule(action="choose_year"),
    )
    for button in months_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=Schedule(
                action=button.action,
                year=chosen_year,
                month=int(button.value),
            ),
        )
    builder.button(
        text=SET_TIME,
        callback_data=Schedule(action="set_time"),
    )
    builder.adjust(1, 4, 4, 4, 1)
    _attach_modify_buttons_for_edit_schedule(builder)
    _attach_footer_buttons_for_schedule(builder, with_view_button=True)
    return builder.as_markup()


def set_schedule_get_days_keyboard(
    chosen_year: int,
    chosen_month: int,
    days_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=months[chosen_month],
        callback_data=Schedule(action="choose_month", year=chosen_year),
    )
    builder.button(
        text=str(chosen_year),
        callback_data=Schedule(action="choose_year"),
    )
    for button in days_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=Schedule(
                action=button.action,
                year=chosen_year,
                month=chosen_month,
                index=int(button.value),
            ),
        )
    builder.adjust(2, 8, 8, 8, 8, 8, 8)
    footer_builder = InlineKeyboardBuilder()
    footer_builder.button(
        text=SET_TIME,
        callback_data=Schedule(action="set_time"),
    )
    footer_builder.adjust(1)
    _attach_modify_buttons_for_edit_schedule(footer_builder)
    _attach_footer_buttons_for_schedule(footer_builder, with_view_button=True)
    builder.attach(footer_builder)
    return builder.as_markup()


def set_schedule_get_times_keyboard(
    times_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in times_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=Schedule(
                action=button.action,
                index=int(button.value),
            ),
        )
    builder.adjust(6)
    footer_builder = InlineKeyboardBuilder()
    footer_builder.button(
        text=SET_DATE,
        callback_data=Schedule(action="choose_day"),
    )
    footer_builder.adjust(1)
    _attach_modify_buttons_for_edit_schedule(footer_builder)
    _attach_footer_buttons_for_schedule(footer_builder, with_view_button=True)
    builder.attach(footer_builder)
    return builder.as_markup()


def get_confirm_clear_schedule_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text=YES, callback_data=Schedule(action="clear_schedule_confirmed"))
    builder.button(text=NO, callback_data=Schedule(action="view_schedule"))
    return builder.as_markup()


def view_schedule_get_years_keyboard(
    years_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in years_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=Schedule(action=button.action, year=int(button.value)),
        )
    builder.adjust(2)
    _attach_edit_schedule_buttons(builder)
    _attach_footer_buttons_for_schedule(builder, with_view_button=False)
    return builder.as_markup()


def view_schedule_get_months_keyboard(
    chosen_year: int,
    months_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=str(chosen_year),
        callback_data=Schedule(action="choose_year"),
    )
    for button in months_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=Schedule(
                action=button.action,
                year=chosen_year,
                month=int(button.value),
            ),
        )
    builder.adjust(1, 4, 4, 4)
    _attach_edit_schedule_buttons(builder)
    _attach_footer_buttons_for_schedule(builder, with_view_button=False)
    return builder.as_markup()


def view_schedule_get_days_keyboard(
    chosen_year: int,
    chosen_month: int,
    days_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in days_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=Schedule(
                action=button.action,
                year=chosen_year,
                month=chosen_month,
                day=int(button.value),
            ),
        )
    builder.adjust(2, 7, 7, 7, 7, 7, 7, 7, 7)
    _attach_edit_schedule_buttons(builder)
    _attach_footer_buttons_for_schedule(builder, with_view_button=False)
    return builder.as_markup()


def view_schedule_get_times_keyboard(
    chosen_year: int,
    chosen_month: int,
    chosen_day: int,
    times_keyboard_buttons: list[InlineButton],
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in times_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=Schedule(
                action=button.action,
                year=chosen_year,
                month=chosen_month,
                day=chosen_day,
                time=button.value,
            ),
        )
    builder.adjust(3, 6, 6, 6, 6, 6, 6, 6, 6)
    _attach_edit_schedule_buttons(builder)
    _attach_footer_buttons_for_schedule(builder, with_view_button=False)
    return builder.as_markup()
