from calendar import Calendar
from datetime import datetime

from src.keyboards import InlineButton
from src.utils import months


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
