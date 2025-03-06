"""Клавиатуры бота."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BACK = "Назад"
MAIN_MENU = "Главная"
SHOW_ID = "Вывести ID"
USLUGI = "Услуги"
CREATE = "Создать"
SHOW_ALL_USLUGI = "Показать все услуги"


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
