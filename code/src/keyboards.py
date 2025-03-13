"""Клавиатуры бота."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BACK = "Назад"
MAIN_MENU = "Главная"
SHOW_ID = "Вывести ID"
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

back_button = KeyboardButton(text=BACK)
main_menu_button = KeyboardButton(text=MAIN_MENU)


admin_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SHOW_ID)],
        [KeyboardButton(text=USLUGI), KeyboardButton(text=ZAPISI)],
    ],
    resize_keyboard=True,
)

client_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SHOW_ID)],
        [KeyboardButton(text=USLUGI), KeyboardButton(text=ZAPISI)],
    ],
    resize_keyboard=True,
)

uslugi_keyboard = ReplyKeyboardMarkup(
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

back_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [back_button],
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


def get_uslugi_to_update_keyboard(names: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [
        [back_button, main_menu_button],
    ]
    arranged_uslugi_names_buttons = _arrange_buttons(names, buttons_in_row=2)
    keyboard.extend(arranged_uslugi_names_buttons)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


usluga_fields_keyboard = ReplyKeyboardMarkup(
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

set_usluga_new_field_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [back_button, main_menu_button],
        [
            KeyboardButton(text=UPDATE_ANOTHER_USLUGA),
        ],
    ],
    resize_keyboard=True,
)


def get_years_keyboard(years: list[int]) -> ReplyKeyboardMarkup:
    years_ = [str(year) for year in years]
    keyboard = [
        [back_button, main_menu_button],
    ]
    arranged_years_buttons = _arrange_buttons(years_, buttons_in_row=2)
    keyboard.extend(arranged_years_buttons)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_months_keyboard(months: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [
        [back_button, main_menu_button],
    ]
    arranged_months_buttons = _arrange_buttons(months, buttons_in_row=4)
    keyboard.extend(arranged_months_buttons)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_days_keyboard(days: list[int]) -> ReplyKeyboardMarkup:
    days_ = [str(day) for day in days]
    keyboard = [
        [back_button, main_menu_button],
    ]
    arranged_days_buttons = _arrange_buttons(days_, buttons_in_row=5)
    keyboard.extend(arranged_days_buttons)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_times_keyboard(times: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [
        [back_button, main_menu_button],
    ]
    arranged_times_buttons = _arrange_buttons(times, buttons_in_row=4)
    keyboard.extend(arranged_times_buttons)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


zapisi_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [back_button],
        [
            KeyboardButton(text=ZAPIS_NA_PRIEM),
            KeyboardButton(text=SHOW_ACTIVE_ZAPISI),
        ],
    ],
    resize_keyboard=True,
)
