"""Клавиатуры бота."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BACK = "Назад"
SHOW_ID = "Вывести ID"
USLUGI = "Услуги"
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
    ],
    resize_keyboard=True,
)
