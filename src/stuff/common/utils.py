"""Вспомогательные функции."""

import re
from datetime import UTC, datetime, tzinfo

import pytz

from src import messages
from src.config import TIMEZONE
from src.constraints import DURATION_MULTIPLIER, MAX_DURATION, MAX_PRICE, USLUGA_NAME_MAX_LEN
from src.stuff.services.exceptions import ServiceNameTooLongError
from src.models import Service, Appointment


ValidationErrorMessage = str


def form_service_view(service: Service, show_duration: bool) -> str:
    view = f"<b>{service.name}</b>\n    <i>Стоимость: {service.price} руб.</i>\n"
    if show_duration:
        view += f"    <i>Длительность: {service.duration} мин.</i>\n"
    return view


def form_services_list_text(services: list[Service], show_duration: bool) -> str:
    text = ""
    for pos, service in enumerate(services, start=1):
        text += f"<b>{pos}.</b> {form_service_view(service, show_duration)}"
    if not text:
        text = messages.NO_SERVICES
    return text.strip()


def preprocess_text(text: str) -> str:
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def validate_service_name(name: str) -> str:
    USLUGA_NAME_SHOULD_BE_SHORTER = (
        f"Название услуги должно содержать не более {USLUGA_NAME_MAX_LEN} символов"
    )
    if len(name) > USLUGA_NAME_MAX_LEN:
        raise ServiceNameTooLongError(USLUGA_NAME_SHOULD_BE_SHORTER)
    return name


def validate_service_price(price_input: str) -> int | ValidationErrorMessage:
    PRICE_SHOULD_BE_INTEGER = "Цена должна быть целым числом"
    PRICE_SHOULD_BE_GT_0 = "Цена должна быть больше 0"
    PRICE_SHOULD_BE_LT_MAX_PRICE = f"Цена должна быть менее {MAX_PRICE} рублей"
    WRONG_FORMAT = "Неверный формат записи числа"
    exponent = r"[eE]"

    price_input = price_input.strip()
    price_input = price_input.replace(",", ".")
    re.sub(r"\.0{2,}$", ".0", price_input)
    if "." in price_input and re.search(r"\.[1-9]+0+$", price_input):
        price_input = price_input.rstrip("0")
    if re.match(r"[+-]*0[^.]", price_input):
        return WRONG_FORMAT
    if re.search(exponent, price_input):
        return WRONG_FORMAT
    if re.fullmatch(r"[+-]?\.\d+", price_input):
        return WRONG_FORMAT
    if re.fullmatch(r"[+-]?\d+\.", price_input):
        return WRONG_FORMAT
    if price_input.count(".") >= 1:
        return PRICE_SHOULD_BE_INTEGER
    if re.search(r"[-+\.\d][-+]", price_input):
        return PRICE_SHOULD_BE_INTEGER
    if re.match(r"\+?\d{7,}\.?\d*", price_input):
        return PRICE_SHOULD_BE_LT_MAX_PRICE
    if re.search(r"[^\d\+\-\.]", price_input):
        return PRICE_SHOULD_BE_INTEGER

    price = int(price_input)
    if price <= 0:
        return PRICE_SHOULD_BE_GT_0
    if price >= MAX_PRICE:
        return PRICE_SHOULD_BE_LT_MAX_PRICE
    return price


def validate_service_duration(duration_input: str) -> int | ValidationErrorMessage:
    DURATION_SHOULD_BE_INTEGER = "Длительность должна быть целым числом"
    DURATION_SHOULD_BE_GT_0 = "Длительность должна быть больше 0"
    DURATION_SHOULD_BE_LT_MAX_DURATION = f"Длительность должна быть менее {MAX_DURATION} минут"
    DURATION_SHOULD_BE_A_MULTIPLE_OF_N = (
        f"Длительность должна быть кратна {DURATION_MULTIPLIER}"
    )
    WRONG_FORMAT = "Неверный формат записи числа"
    exponent = r"[eE]"

    duration_input = duration_input.strip()
    duration_input = duration_input.replace(",", ".")
    re.sub(r"\.0{2,}$", ".0", duration_input)
    if "." in duration_input and re.search(r"\.[1-9]+0+$", duration_input):
        duration_input = duration_input.rstrip("0")
    if re.match(r"[+-]*0[^.]", duration_input):
        return WRONG_FORMAT
    if re.search(exponent, duration_input):
        return WRONG_FORMAT
    if re.fullmatch(r"[+-]?\.\d+", duration_input):
        return WRONG_FORMAT
    if re.fullmatch(r"[+-]?\d+\.", duration_input):
        return WRONG_FORMAT
    if duration_input.count(".") >= 1:
        return DURATION_SHOULD_BE_INTEGER
    if re.search(r"[-+\.\d][-+]", duration_input):
        return DURATION_SHOULD_BE_INTEGER
    if re.match(r"\+?\d{4,}\.?\d*", duration_input):
        return DURATION_SHOULD_BE_LT_MAX_DURATION
    if re.search(r"[^\d\+\-\.]", duration_input):
        return DURATION_SHOULD_BE_INTEGER

    duration = int(duration_input)
    if duration <= 0:
        return DURATION_SHOULD_BE_GT_0
    if duration >= MAX_DURATION:
        return DURATION_SHOULD_BE_LT_MAX_DURATION
    if (duration % DURATION_MULTIPLIER) != 0:
        return DURATION_SHOULD_BE_A_MULTIPLE_OF_N
    return duration


months = {
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
months_swapped = {value: key for key, value in months.items()}


def dates_to_lang(
    year: int | None,
    month: int | None = None,
    day: int | None = None,
    week: int | None = None,
    day_of_week: int | None = None,
) -> str:
    """
    Текстовое представление даты (как мы говорим).

    get_lang_date(2020) -> "2020 год"
    get_lang_date(2020, 4) -> "Апрель 2020 года"
    get_lang_date(2020, 4, 22) -> "22 апреля 2020 года"
    get_lang_date(2020, 4, 22, 3) -> "3я неделя апреля 2020 года"
    get_lang_date(2020, 4, 22, 3, 5) -> "Пятницы апреля 2020 года"
    """
    if week:
        assert year
        assert month
        assert not day
        assert not day_of_week
    if day_of_week:
        assert year
        assert month
        assert not day
        assert not week
    lang_date = ""
    if year and month and day:
        month_name = months[month]
        if month_name.endswith("т"):
            month_name_genitive = month_name + "а"
        else:
            month_name_genitive = month_name[:-1] + "я"
        lang_date = f"{day} {month_name_genitive.lower()} {year} года"
    elif year and month:
        if week or day_of_week:
            month_name = months[month]
            if month_name.endswith("т"):
                month_name_genitive = month_name + "а"
            else:
                month_name_genitive = month_name[:-1] + "я"
            if week:
                lang_date = f"{week}я неделя {month_name_genitive.lower()} {year} года"
            elif day_of_week:
                days_of_week_plural = {
                    1: "Понедельники",
                    2: "Вторники",
                    3: "Среды",
                    4: "Четверги",
                    5: "Пятницы",
                    6: "Субботы",
                    7: "Воскресенья",
                }
                lang_date = f"{days_of_week_plural[day_of_week]} {month_name_genitive.lower()} {year} года"
        else:
            month_name = months[month]
            lang_date = f"{month_name} {year} года"
    elif year:
        lang_date = f"{year} год"
    return lang_date


def form_appointment_view(appointment: Appointment, with_date: bool, for_admin: bool) -> str:
    view = ""
    tz_starts_at = from_utc(appointment.starts_at, TIMEZONE)
    if with_date:
        date_ = tz_starts_at.strftime("%d.%m.%Y")
        view += f"<b>{date_}</b>\n"
    start_time = tz_starts_at.strftime("%H:%M")
    if for_admin:
        tz_ends_at = from_utc(appointment.ends_at, TIMEZONE)
        end_time = tz_ends_at.strftime("%H:%M")
        view += f"    <i>{start_time} - {end_time}</i>  {appointment.service.name}\n"
    else:
        view += f"    <i>{start_time}</i>  {appointment.service.name}\n"
    return view


def form_appointments_list_text(appointments: list[Appointment], for_admin: bool) -> str:
    appointments_dict = dict()
    for appointment in appointments:
        date_ = appointment.starts_at.strftime("%d.%m.%Y")
        if date_ in appointments_dict:
            appointments_dict[date_].append(appointment)
        else:
            appointments_dict[date_] = [appointment]
    text = ""
    for date_, appointments_ in appointments_dict.items():
        text += f"<b>{date_}</b>\n"
        for appointment in appointments_:
            text += f"{form_appointment_view(appointment, with_date=False, for_admin=for_admin)}"
    if not text:
        if for_admin:
            text = messages.NO_APPOINTMENTS_FOR_ADMIN
        else:
            text = messages.NO_APPOINTMENTS_FOR_CLIENT
    return text.strip()


def from_utc(utc_dt: datetime, dest_tz: tzinfo) -> datetime:
    if not utc_dt.tzinfo:
        utc_dt = pytz.timezone("UTC").localize(utc_dt)
    tz_datetime = utc_dt.astimezone(dest_tz)
    return tz_datetime


def to_utc(tz_dt: datetime) -> datetime:
    utc_tz = pytz.timezone("UTC")
    utc_datetime = tz_dt.astimezone(utc_tz)
    return utc_datetime


def get_utc_now() -> datetime:
    utc_now = datetime.now(UTC)
    return utc_now


def get_years_with_months(
    slots: dict[int, dict[int, dict[int, list[str]]]],
) -> dict[int, list[int]]:
    years_with_months = {year: list(dict_.keys()) for year, dict_ in slots.items()}
    return years_with_months


def get_years_with_months_days(
    slots: dict[int, dict[int, dict[int, list[str]]]],
) -> dict[int, dict[int, list[int]]]:
    years_with_months_days = {}
    for year, dict_ in slots.items():
        years_with_months_days[year] = {}
        for month, dict__ in dict_.items():
            years_with_months_days[year][month] = list(dict__.keys())
    return years_with_months_days
