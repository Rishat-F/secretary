"""Вспомогательные функции."""

import re
from calendar import Calendar
from datetime import date

from src.constraints import DURATION_MULTIPLIER, USLUGA_NAME_MAX_LEN
from src.messages import NO_USLUGI, NO_ZAPISI_FOR_ADMIN, NO_ZAPISI_FOR_CLIENT
from src.models import Usluga, Zapis

from src.exceptions import UslugaNameTooLongError


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


_months = {
    1: "Январь",
    2: "Февраль",
    3: "Март",
    4: "Апрель",
    5: "Май",
    6: "Июнь",
    7: "Июль",
    8: "Август",
    9: "Сентябрь",
    10: "Октябрь",
    11: "Ноябрь",
    12: "Декабрь",
}
months_swapped = {value: key for key, value in _months.items()}


def get_months(year: int) -> list[str]:
    today = date.today()
    if year == today.year:
        current_month_num = today.month
        result = []
        for num, name in _months.items():
            if num >= current_month_num:
                result.append(name)
        return result
    else:
        return list(_months.values())


def get_days(year: int, month: str) -> list[int]:
    month_num = months_swapped[month]
    today = date.today()
    calendar = Calendar()
    if month_num == today.month:
        days = [
            number for number in calendar.itermonthdays(year, month_num)
            if (number != 0 and number >= today.day)
        ]
    else:
        days = [
            number for number in calendar.itermonthdays(year, month_num)
            if number != 0
        ]
    return days


def get_available_times(*_) -> list[str]:
    all_times = [
        "00:00", "00:30", "01:00", "01:30",
        "02:00", "02:30", "03:00", "03:30",
        "04:00", "04:30", "05:00", "05:30",
        "06:00", "06:30", "07:00", "07:30",
        "08:00", "08:30", "09:00", "09:30",
        "10:00", "10:30", "11:00", "11:30",
        "12:00", "12:30", "13:00", "13:30",
        "14:00", "14:30", "15:00", "15:30",
        "16:00", "16:30", "17:00", "17:30",
        "18:00", "18:30", "19:00", "19:30",
        "20:00", "20:30", "21:00", "21:30",
        "22:00", "22:30", "23:00", "23:30",
    ]
    available_times = all_times
    return available_times


def form_zapis_view(zapis: Zapis, with_date: bool, for_admin: bool) -> str:
    view = ""
    if with_date:
        date_ = zapis.starts_at.strftime("%d.%m.%Y")
        view += f"<b>{date_}</b>\n"
    start_time = zapis.starts_at.strftime("%H:%M")
    if for_admin:
        end_time = zapis.ends_at.strftime("%H:%M")
        view += f"    <i>{start_time} - {end_time}</i>  {zapis.usluga.name}\n"
    else:
        view += f"    <i>{start_time}</i>  {zapis.usluga.name}\n"
    return view


def form_zapisi_list_text(zapisi: list[Zapis], for_admin: bool) -> str:
    zapisi_dict = dict()
    for zapis in zapisi:
        date_ = zapis.starts_at.strftime("%d.%m.%Y")
        if date_ in zapisi_dict:
            zapisi_dict[date_].append(zapis)
        else:
            zapisi_dict[date_] = [zapis]
    text = ""
    for date_, zapisi_ in zapisi_dict.items():
        text += f"<b>{date_}</b>\n"
        for zapis in zapisi_:
            text += f"{form_zapis_view(zapis, with_date=False, for_admin=for_admin)}"
    if not text:
        if for_admin:
            text = NO_ZAPISI_FOR_ADMIN
        else:
            text = NO_ZAPISI_FOR_CLIENT
    return text.strip()
