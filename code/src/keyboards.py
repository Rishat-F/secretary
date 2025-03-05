"""Клавиатуры бота."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

SHOW_ID = "Вывести ID"


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SHOW_ID)],
    ],
    resize_keyboard=True,
)
