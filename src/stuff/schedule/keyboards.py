from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.stuff.common.keyboards import MAIN_MENU, NO, YES, InlineButton
from src.stuff.common.utils import months


CLEAR = "Обнулить"
MODIFY = "Изменить"
SAVE = "Сохранить"
DELETE = "Удалить"
SET_TIME = "Задать время"
SET_DATE = "Задать даты"
VIEW = "Просмотр"


class Schedule(CallbackData, prefix="schedule", sep="$"):
    action: str
    year: int | None = None
    month: int | None = None
    day: int | None = None
    week: int | None = None
    day_of_week: int | None = None
    time: str | None = None
    index: int | None = None


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
    day_counter = 1
    week_counter = 1
    for button in days_keyboard_buttons:
        if button.text == "✖️":
            chosen_day = day_counter
            day_counter += 1
        else:
            chosen_day = None
        if button.text == "➞":
            chosen_week = week_counter
            week_counter += 1
        else:
            chosen_week = None
        if button.text == "Пн":
            chosen_day_of_week = 1
        elif button.text == "Вт":
            chosen_day_of_week = 2
        elif button.text == "Ср":
            chosen_day_of_week = 3
        elif button.text == "Чт":
            chosen_day_of_week = 4
        elif button.text == "Пт":
            chosen_day_of_week = 5
        elif button.text == "Сб":
            chosen_day_of_week = 6
        elif button.text == "Вс":
            chosen_day_of_week = 7
        else:
            chosen_day_of_week = None
        builder.button(
            text=button.text,
            callback_data=Schedule(
                action=button.action,
                year=chosen_year,
                month=chosen_month,
                day=chosen_day,
                week=chosen_week,
                day_of_week=chosen_day_of_week,
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
