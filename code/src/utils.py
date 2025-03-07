"""Вспомогательные функции."""

import re

from constraints import DURATION_MULTIPLIER, USLUGA_NAME_MAX_LEN
from messages import NO_USLUGI
from models import Usluga

from exceptions import UslugaNameTooLongError


ValidationErrorMessage = str


def form_usluga_view(usluga: Usluga, show_duration: bool) -> str:
    view = f"<b>{usluga.name}</b>\n    <i>Стоимость: {usluga.price} руб.</i>\n"
    if show_duration:
        view += f"    <i>Длительность: {usluga.duration} мин.</i>\n"
    return view


def form_uslugi_list_text(uslugi: list[Usluga], show_duration: bool) -> str:
    text = ""
    for pos, usluga in enumerate(uslugi, start=1):
        text += f"<b>{pos}.</b> {form_usluga_view(usluga, show_duration)}"
    if not text:
        text = NO_USLUGI
    return text.strip()


def preprocess_text(text: str) -> str:
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def validate_usluga_name(name: str) -> str:
    USLUGA_NAME_SHOULD_BE_SHORTER = (
        f"Название услуги должно содержать не более {USLUGA_NAME_MAX_LEN} символов"
    )
    if len(name) > USLUGA_NAME_MAX_LEN:
        raise UslugaNameTooLongError(USLUGA_NAME_SHOULD_BE_SHORTER)
    return name


def validate_usluga_price(price_input: str) -> int | ValidationErrorMessage:
    PRICE_SHOULD_BE_INTEGER = "Цена должна быть целым числом"
    PRICE_SHOULD_BE_GT_0 = "Цена должна быть больше 0"
    try:
        price = int(price_input)
    except ValueError:
        return PRICE_SHOULD_BE_INTEGER
    if price <= 0:
        return PRICE_SHOULD_BE_GT_0
    return price


def validate_usluga_duration(duration_input: str) -> int | ValidationErrorMessage:
    DURATION_SHOULD_BE_INTEGER = "Длительность должна быть целым числом"
    DURATION_SHOULD_BE_GT_0 = "Длительность должна быть больше 0"
    DURATION_MUST_BE_A_MULTIPLE_OF_N = (
        f"Длительность должна быть кратна {DURATION_MULTIPLIER}"
    )
    try:
        duration = int(duration_input)
    except ValueError:
        return DURATION_SHOULD_BE_INTEGER
    if duration <= 0:
        return DURATION_SHOULD_BE_GT_0
    if (duration % DURATION_MULTIPLIER) != 0:
        return DURATION_MUST_BE_A_MULTIPLE_OF_N
    return duration
