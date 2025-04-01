"""Вспомогательные функции."""

import re
from datetime import datetime, timedelta

from src.constraints import DURATION_MULTIPLIER, USLUGA_NAME_MAX_LEN
from src.messages import NO_SERVICES, NO_APPOINTMENTS_FOR_ADMIN, NO_APPOINTMENTS_FOR_CLIENT
from src.models import Service, Appointment

from src.exceptions import ServiceNameTooLongError


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
        text = NO_SERVICES
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
    try:
        price = int(price_input)
    except ValueError:
        return PRICE_SHOULD_BE_INTEGER
    if price <= 0:
        return PRICE_SHOULD_BE_GT_0
    return price


def validate_service_duration(duration_input: str) -> int | ValidationErrorMessage:
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


def get_years(slots: dict[int, dict[int, dict[int, list[str]]]]) -> list[int]:
    years = sorted(slots.keys())
    return years


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


def get_months(
    slots: dict[int, dict[int, dict[int, list[str]]]],
    year: int,
) -> list[str]:
    months = [_months[month_num] for month_num in slots[year].keys()]
    return months


def get_days(
    slots: dict[int, dict[int, dict[int, list[str]]]],
    year: int,
    month: str,
) -> list[int]:
    month_num = months_swapped[month]
    days = list(slots[year][month_num].keys())
    return days


def get_times(
    slots: dict[int, dict[int, dict[int, list[str]]]],
    year: int,
    month: str,
    day: int,
) -> list[str]:
    month_num = months_swapped[month]
    times = slots[year][month_num][day]
    return times


def form_appointment_view(appointment: Appointment, with_date: bool, for_admin: bool) -> str:
    view = ""
    if with_date:
        date_ = appointment.starts_at.strftime("%d.%m.%Y")
        view += f"<b>{date_}</b>\n"
    start_time = appointment.starts_at.strftime("%H:%M")
    if for_admin:
        end_time = appointment.ends_at.strftime("%H:%M")
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
            text = NO_APPOINTMENTS_FOR_ADMIN
        else:
            text = NO_APPOINTMENTS_FOR_CLIENT
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
