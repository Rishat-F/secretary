"""Клавиатуры бота."""

from datetime import datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.utils import InlineButton

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

back_button = KeyboardButton(text=BACK)
main_menu_button = KeyboardButton(text=MAIN_MENU)


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=USLUGI), KeyboardButton(text=ZAPISI)],
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


class DateTimePicker(CallbackData, prefix="pick_datetime", sep="$"):
    action: str 
    year: int | None = None
    month: int | None = None
    day: int | None = None
    time: str | None = None


def get_years_keyboard(years_keyboard_buttons: list[InlineButton]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for button in years_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=DateTimePicker(action=button.action, year=int(button.value)),
        )
    builder.adjust(3)
    footer_builder = InlineKeyboardBuilder()
    footer_builder.button(
        text=CANCEL,
        callback_data=DateTimePicker(action="cancel"),
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
        callback_data=DateTimePicker(action="choose_year"),
    )
    for button in months_keyboard_buttons:
        builder.button(
            text=button.text,
            callback_data=DateTimePicker(
                action=button.action,
                year=chosen_year,
                month=int(button.value),
            ),
        )
    builder.button(
        text=CANCEL,
        callback_data=DateTimePicker(action="cancel"),
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
            callback_data=DateTimePicker(
                action=button.action,
                year=chosen_year,
                month=chosen_month,
                day=int(button.value),
            ),
        )
    builder.button(
        text=CANCEL,
        callback_data=DateTimePicker(action="cancel"),
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
            callback_data=DateTimePicker(
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
        callback_data=DateTimePicker(action="cancel"),
    )
    builder.attach(footer_builder)
    return builder.as_markup()


def get_confirm_appointment_keyboard(chosen_datetime: datetime) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=YES,
        callback_data=DateTimePicker(
            action="confirmed",
            year=chosen_datetime.year,
            month=chosen_datetime.month,
            day=chosen_datetime.day,
            time=chosen_datetime.time().isoformat(timespec="minutes"),
        ),
    )
    builder.button(
        text=NO, callback_data=DateTimePicker(
            action="choose_time",
            year=chosen_datetime.year,
            month=chosen_datetime.month,
            day=chosen_datetime.day,
        ),
    )
    builder.button(text=CANCEL, callback_data=DateTimePicker(action="cancel"))
    builder.adjust(1, 1, 1)
    return builder.as_markup()
