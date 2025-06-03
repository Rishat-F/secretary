from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from src.stuff.common.keyboards import back_button, main_menu_button


CREATE = "Создать"
UPDATE = "Изменить"
DELETE = "Удалить"
SHOW_ALL_USLUGI = "Показать все услуги"
NAME = "Название"
PRICE = "Стоимость"
DURATION = "Длительность"
UPDATE_ANOTHER_USLUGA = "Изменить другую услугу"


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
