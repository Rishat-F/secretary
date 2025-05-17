from calendar import Calendar
from datetime import datetime, time

from src.constraints import DURATION_MULTIPLIER
from src.keyboards import InlineButton
from src.utils import months


MINIMAL_ALL_TIMES_LEN = 3


def get_schedule_times(slots_datetimes: list[datetime]) -> list[str]:
    times = []
    for slot_datetime in slots_datetimes:
        times.append(slot_datetime.time().isoformat(timespec="minutes"))
    return times


def view_schedule_get_years_keyboard_buttons(
    years: list[int],
    now_: datetime,
) -> list[InlineButton]:
    result = []
    current_year = now_.year
    years_to_choose = [year_ for year_ in years if year_ >= current_year]
    if not years_to_choose:
        return result
    for year in years_to_choose:
        if year == current_year:
            text = f"[ {year} ]"
        else:
            text = str(year)
        result.append(InlineButton(action="choose_month", text=text, value=str(year)))
    return result


def view_schedule_get_months_keyboard_buttons(
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
                result.append(InlineButton("ignore", " ", str(month_num)))
            elif month_num == current_month and month_num not in available_months:
                result.append(InlineButton("ignore", " ", str(month_num)))
            elif month_num == current_month and month_num in available_months:
                result.append(InlineButton("view_schedule", f"[ {month_name} ]", str(month_num)))
            elif month_num not in available_months:
                result.append(InlineButton("ignore", " ", str(month_num)))
            else:
                result.append(InlineButton("view_schedule", month_name, str(month_num)))
    else:
        for month_num, month_name in months.items():
            if month_num not in available_months:
                result.append(InlineButton("ignore", " ", str(month_num)))
            else:
                result.append(InlineButton("view_schedule", month_name, str(month_num)))
    return result


def view_schedule_get_days_keyboard_buttons(
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
    result.append(InlineButton("choose_month", str(months[chosen_month]), str(chosen_month)))
    result.append(InlineButton("choose_year", str(chosen_year), str(chosen_year)))
    week_days_names = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    for week_day_name in week_days_names:
        result.append(InlineButton("ignore", week_day_name, str(0)))
    for month_day_number in calendar.itermonthdays(chosen_year, chosen_month):
        if month_day_number == 0:
            text = " "
            action = "ignore"
        elif chosen_year == current_year and chosen_month == current_month:
            if month_day_number < current_day:
                text = " "
                action = "ignore"
            elif month_day_number not in available_days:
                text = " "
                action = "ignore"
            else:
                text = str(month_day_number)
                action = "choose_time"
            if month_day_number == current_day:
                if len(text) == 1:
                    text = f"[ {text} ]"
                else:
                    text = f"[{text}]"
        elif month_day_number not in available_days:
            text = " "
            action = "ignore"
        else:
            text = str(month_day_number)
            action = "choose_time"
        result.append(InlineButton(action, text, str(month_day_number)))
    return result


def get_all_times_len(duration_multiplier: int) -> int:
    all_times_len = (24 * 60) // duration_multiplier + 1
    return all_times_len


def _get_all_times(duration_multiplier: int) -> list[str]:
    all_times = []
    total_minutes = 0
    all_times_len = get_all_times_len(duration_multiplier)
    for _ in range(all_times_len):
        hours = (total_minutes // 60) % 24
        minutes = total_minutes % 60
        time_ = time(hours, minutes)
        all_times.append(time_.isoformat(timespec="minutes"))
        total_minutes += duration_multiplier
    return all_times


def _get_schedule_times_from_to(
    schedule_times: list[str],
    duration_multiplier: int,
) -> list[str]:
    assert schedule_times
    schedule_times = sorted(schedule_times)
    schedule_times_from_to = []
    for i in range(len(schedule_times)):
        current_element = schedule_times[i]
        schedule_times_from_to.append(current_element)
        try:
            next_element = schedule_times[i+1]
        except IndexError:
            next_element = None
        current_element_time = time.fromisoformat(current_element)
        current_element_total_minutes = current_element_time.hour * 60 + current_element_time.minute
        if next_element is None:
            total_minutes = current_element_total_minutes + duration_multiplier
            hours = (total_minutes // 60) % 24
            minutes = total_minutes % 60
            time_ = time(hours, minutes)
            schedule_times_from_to.append(time_.isoformat(timespec="minutes"))
        else:
            next_element_time = time.fromisoformat(next_element)
            next_element_total_minutes = next_element_time.hour * 60 + next_element_time.minute
            if (next_element_total_minutes - current_element_total_minutes) != duration_multiplier:
                total_minutes = current_element_total_minutes + duration_multiplier
                hours = (total_minutes // 60) % 24
                minutes = total_minutes % 60
                time_ = time(hours, minutes)
                schedule_times_from_to.append(time_.isoformat(timespec="minutes"))
    return schedule_times_from_to


def _get_times_buttons_for_view_schedule(
    all_times: list[str],
    schedule_times_from_to: list[str],
) -> list[InlineButton]:
    assert len(all_times) >= MINIMAL_ALL_TIMES_LEN
    assert all_times[0] == "00:00"
    assert all_times[-1] == "00:00"
    assert schedule_times_from_to
    times_buttons = []
    if schedule_times_from_to[0] == "00:00":
        times_buttons.append(InlineButton("ignore", "00:00", "00:00"))
    else:
        times_buttons.append(InlineButton("ignore", " ", "00:00"))
    for time_ in all_times[1:-1]:
        if time_ in schedule_times_from_to:
            text = time_
        else:
            text = " "
        times_buttons.append(InlineButton("ignore", text, time_))
    if schedule_times_from_to[-1] == "00:00":
        times_buttons.append(InlineButton("ignore", "00:00", "00:00"))
    else:
        times_buttons.append(InlineButton("ignore", " ", "00:00"))
    return times_buttons


def view_schedule_get_times_keyboard_buttons(
    schedule: dict[int, dict[int, dict[int, list[str]]]],
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
    assert chosen_year in schedule
    assert chosen_month in schedule[chosen_year]
    assert chosen_day in schedule[chosen_year][chosen_month]
    current_time = now_.time().isoformat(timespec="minutes")
    if chosen_year == current_year and chosen_month == current_month and chosen_day == current_day:
        schedule_times = [
            time_ for time_ in schedule[chosen_year][chosen_month][chosen_day]
            if time_ > current_time
        ]
    else:
        schedule_times = [time_ for time_ in schedule[chosen_year][chosen_month][chosen_day]]
    all_times = _get_all_times(DURATION_MULTIPLIER)
    result = []
    result.append(InlineButton("view_schedule", str(chosen_day), str(chosen_day)))
    result.append(InlineButton("choose_month", str(months[chosen_month]), str(chosen_month)))
    result.append(InlineButton("choose_year", str(chosen_year), str(chosen_year)))
    schedule_times_from_to = _get_schedule_times_from_to(schedule_times, DURATION_MULTIPLIER)
    times_buttons = _get_times_buttons_for_view_schedule(all_times, schedule_times_from_to)
    result.extend(times_buttons)
    return result
