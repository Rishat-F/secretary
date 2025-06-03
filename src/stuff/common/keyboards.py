from typing import NamedTuple

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


BACK = "Назад"
MAIN_MENU = "Главная"
CANCEL = "Отмена"
YES = "Да"
NO = "Нет"

back_button = KeyboardButton(text=BACK)
main_menu_button = KeyboardButton(text=MAIN_MENU)


class InlineButton(NamedTuple):
    action: str
    text: str
    value: str


back_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [back_button, main_menu_button],
    ],
    resize_keyboard=True,
)
