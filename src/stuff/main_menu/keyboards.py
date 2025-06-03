from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


USLUGI = "Услуги"
ZAPISI = "Записи"
SCHEDULE = "График работы"


def get_main_keyboard(for_admin: bool) -> ReplyKeyboardMarkup:
    keyboard_=[
        [KeyboardButton(text=USLUGI), KeyboardButton(text=ZAPISI)],
    ]
    if for_admin:
        keyboard_.append([KeyboardButton(text=SCHEDULE)])
    keyboard = ReplyKeyboardMarkup(keyboard=keyboard_, resize_keyboard=True)
    return keyboard


