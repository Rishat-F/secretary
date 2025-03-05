"""Клавиатуры бота."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

SHOW_ID = "Вывести ID"
USLUGI = "Услуги"


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SHOW_ID)],
        [KeyboardButton(text=USLUGI)],
    ],
    resize_keyboard=True,
)
