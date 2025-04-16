"""Вспомогательные функции."""

import re
from calendar import Calendar
from datetime import UTC, datetime, timedelta, tzinfo
from typing import NamedTuple

import pytz

from src import messages
from src.config import TIMEZONE
from src.constraints import DURATION_MULTIPLIER, MAX_DURATION, MAX_PRICE, USLUGA_NAME_MAX_LEN
from src.exceptions import (
    DayBecomeNotAvailable,
    MonthBecomeNotAvailable,
    ServiceNameTooLongError,
    TimeBecomeNotAvailable,
    YearBecomeNotAvailable,
)
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
    DURATION_MUST_BE_A_MULTIPLE_OF_N = (
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
        return DURATION_MUST_BE_A_MULTIPLE_OF_N
    return duration


class InlineButton(NamedTuple):
    action: str
    text: str
    value: str


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


def get_years_keyboard_buttons(years: list[int], now_: datetime) -> list[InlineButton]:
    result = []
    current_year = now_.year
    years_to_choose = [year_ for year_ in years if year_ >= current_year]
    if not years_to_choose:
        return result
    first_year_to_choose, *other_years = years_to_choose
    if current_year != first_year_to_choose:
        result.append(
            InlineButton(action="not_available", text="[ ✖️ ]", value=current_year),
        )
        for year_ in range(current_year + 1, first_year_to_choose):
            result.append(
                InlineButton(action="not_available", text="✖️", value=year_),
            )
        result.append(
            InlineButton(
                action="choose_month",
                text=str(first_year_to_choose),
                value=first_year_to_choose,
            ),
        )
    else:
        result.append(
            InlineButton(
                action="choose_month",
                text=f"[ {first_year_to_choose} ]",
                value=first_year_to_choose,
            ),
        )
        if other_years and (other_years[0] - current_year) == 1:
            result.append(
                InlineButton(
                    action="choose_month",
                    text=str(other_years[0]),
                    value=other_years[0],
                ),
            )
    return result


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


def date_to_lang(year: int | None, month: int | None = None, day: int | None = None) -> str:
    """
    Текстовое представление даты (как мы говорим).

    get_lang_date(2020) -> "2020 год"
    get_lang_date(2020, 4) -> "Апрель 2020 года"
    get_lang_date(2020, 4, 22) -> "22 апреля 2020 года"
    """
    lang_date = ""
    if year and month and day:
        month_name = months[month]
        if month_name.endswith("т"):
            month_name_genitive = month_name + "а"
        else:
            month_name_genitive = month_name[:-1] + "я"
        lang_date = f"{day} {month_name_genitive.lower()} {year} года"
    elif year and month:
        month_name = months[month]
        lang_date = f"{month_name} {year} года"
    elif year:
        lang_date = f"{year} год"
    return lang_date


def get_months_keyboard_buttons(
    years_with_months: dict[int, list[int]],
    now_: datetime,
    chosen_year: int,
) -> list[InlineButton]:
    current_year = now_.year
    current_month = now_.month
    assert chosen_year >= current_year
    assert chosen_year in years_with_months
    available_months = years_with_months[chosen_year]
    result = []
    if chosen_year == current_year:
        for month_num, month_name in months.items():
            if month_num < current_month:
                result.append(InlineButton("ignore", " ", month_num))
            elif month_num == current_month and month_num not in available_months:
                result.append(InlineButton("not_available", "[ ✖️ ]", month_num))
            elif month_num == current_month and month_num in available_months:
                result.append(InlineButton("choose_day", f"[ {month_name} ]", month_num))
            elif month_num not in available_months:
                result.append(InlineButton("not_available", "✖️", month_num))
            else:
                result.append(InlineButton("choose_day", month_name, month_num))
    else:
        for month_num, month_name in months.items():
            if month_num not in available_months:
                result.append(InlineButton("not_available", "✖️", month_num))
            else:
                result.append(InlineButton("choose_day", month_name, month_num))
    return result


def get_days_keyboard_buttons(
    years_with_months_days: dict[int, dict[int, list[int]]],
    now_: datetime,
    chosen_year: int | None = None,
    chosen_month: int | None = None,
) -> list[InlineButton]:
    current_year = now_.year
    current_month = now_.month
    current_day = now_.day
    if chosen_year is None:
        assert chosen_month is None
        chosen_year = min(years_with_months_days.keys())
    if chosen_month is None:
        chosen_month = min(years_with_months_days[chosen_year])
    assert chosen_year >= current_year
    if chosen_year == current_year:
        assert chosen_month >= current_month
    assert chosen_year in years_with_months_days
    assert chosen_month in years_with_months_days[chosen_year]
    available_days = years_with_months_days[chosen_year][chosen_month]
    result = []
    calendar = Calendar()
    result.append(InlineButton("choose_month", str(months[chosen_month]), chosen_month))
    result.append(InlineButton("choose_year", str(chosen_year), chosen_year))
    week_days_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    for week_day_name in week_days_names:
        result.append(InlineButton("ignore", week_day_name, 0))
    for month_day_number in calendar.itermonthdays(chosen_year, chosen_month):
        if month_day_number == 0:
            text = " "
            action = "ignore"
        elif chosen_year == current_year and chosen_month == current_month:
            if month_day_number < current_day:
                text = " "
                action = "ignore"
            elif month_day_number not in available_days:
                text = "✖️"
                action = "not_available"
            else:
                text = str(month_day_number)
                action = "choose_time"
            if month_day_number == current_day:
                if len(text) == 1:
                    text = f"[ {text} ]"
                else:
                    text = f"[{text}]"
        elif month_day_number not in available_days:
            text = "✖️"
            action = "not_available"
        else:
            text = str(month_day_number)
            action = "choose_time"
        result.append(InlineButton(action, text, month_day_number))
    return result


def get_times_keyboard_buttons(
    slots: dict[int, dict[int, dict[int, list[str]]]],
    now_: datetime,
    chosen_year: int,
    chosen_month: int,
    chosen_day: int,
) -> list[InlineButton]:
    current_year = now_.year
    current_month = now_.month
    current_day = now_.day
    assert chosen_year >= current_year
    if chosen_year == current_year:
        assert chosen_month >= current_month
    if chosen_year == current_year and chosen_month == current_month:
        assert chosen_day >= current_day
    assert chosen_year in slots
    assert chosen_month in slots[chosen_year]
    assert chosen_day in slots[chosen_year][chosen_month]
    current_time = now_.time().isoformat(timespec="minutes")
    if chosen_year == current_year and chosen_month == current_month and chosen_day == current_day:
        available_times = [
            time_ for time_ in slots[chosen_year][chosen_month][chosen_day]
            if time_ > current_time
        ]
    else:
        available_times = [time_ for time_ in slots[chosen_year][chosen_month][chosen_day]]
    result = []
    result.append(InlineButton("choose_day", str(chosen_day), chosen_day))
    result.append(InlineButton("choose_month", str(months[chosen_month]), chosen_month))
    result.append(InlineButton("choose_year", str(chosen_year), chosen_year))
    for time_ in available_times:
        result.append(InlineButton("confirm", time_, time_))
    return result


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


def get_datetimes_needed_for_appointment(starts_at: datetime, duration: int) -> list[datetime]:
    needed_datetimes = [starts_at]
    slots_needed = int(duration / DURATION_MULTIPLIER)
    for i in range(1, slots_needed):
        needed_datetimes.append(starts_at + timedelta(minutes=DURATION_MULTIPLIER * i))
    return needed_datetimes


def get_times_for_appointment(
    slots_datetimes: list[datetime],
    service_duration: int,
) -> list[str]:
    possible_times = []
    for slot_datetime in slots_datetimes:
        needed_datetimes = get_datetimes_needed_for_appointment(slot_datetime, service_duration)
        if all([needed_datetime in slots_datetimes for needed_datetime in needed_datetimes]):
            possible_times.append(slot_datetime.time().isoformat(timespec="minutes"))
    return possible_times


def check_chosen_datetime_is_possible(
    datetime_: datetime,
    slots: dict[int, dict[int, dict[int, list[str]]]],
) -> None:
    """Вызывает исключение если дата и время недоступно для записи, иначе возвращает None."""
    if datetime_.year not in slots:
        raise YearBecomeNotAvailable(
            messages.YEAR_BECOME_NOT_AVAILABLE.format(lang_year=date_to_lang(datetime_.year)),
        )
    elif datetime_.month not in slots[datetime_.year]:
        raise MonthBecomeNotAvailable(
            messages.MONTH_BECOME_NOT_AVAILABLE.format(
                lang_month_year=date_to_lang(datetime_.year, datetime_.month),
            ),
        )
    elif datetime_.day not in slots[datetime_.year][datetime_.month]:
        raise DayBecomeNotAvailable(
            messages.DAY_BECOME_NOT_AVAILABLE.format(
                lang_day_month_year=date_to_lang(datetime_.year, datetime_.month, datetime_.day),
            ),
        )
    elif datetime_.time().isoformat(timespec="minutes") not in slots[datetime_.year][datetime_.month][datetime_.day]:
        raise TimeBecomeNotAvailable(
            messages.TIME_BECOME_NOT_AVAILABLE.format(time=datetime_.time().isoformat(timespec="minutes")),
        )
    else:
        return None


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
