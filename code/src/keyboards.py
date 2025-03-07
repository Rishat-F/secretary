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


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SHOW_ID)],
        [KeyboardButton(text=USLUGI)],
    ],
    resize_keyboard=True,
)

uslugi_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=BACK),
            KeyboardButton(text=SHOW_ALL_USLUGI),
        ],
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
        [
            KeyboardButton(text=BACK),
            KeyboardButton(text=MAIN_MENU),
        ],
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
        [
            KeyboardButton(text=BACK),
            KeyboardButton(text=MAIN_MENU),
        ],
    ]
    arranged_uslugi_names_buttons = _arrange_buttons(names, buttons_in_row=2)
    keyboard.extend(arranged_uslugi_names_buttons)
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


usluga_fields_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=BACK),
            KeyboardButton(text=MAIN_MENU),
        ],
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
        [
            KeyboardButton(text=BACK),
            KeyboardButton(text=MAIN_MENU),
        ],
        [
            KeyboardButton(text=UPDATE_ANOTHER_USLUGA),
        ],
    ],
    resize_keyboard=True,
)
