from calendar import Calendar
from datetime import datetime, time, timedelta

from src import messages
from src.constraints import DURATION_MULTIPLIER
from src.exceptions import (
    DayBecomeNotAvailable,
    MonthBecomeNotAvailable,
    TimeBecomeNotAvailable,
    YearBecomeNotAvailable,
)
from src.keyboards import InlineButton
from src.utils import date_to_lang, months


def _get_times_statuses_len(duration_multiplier: int) -> int:
    times_statuses_len = (24 * 60) // duration_multiplier + 1
    return times_statuses_len


TIMES_STATUSES_LEN = _get_times_statuses_len(DURATION_MULTIPLIER)
MINIMAL_TIMES_STATUSES_LEN = 3


class ScheduleTimeStatus:
    NOT_SELECTED = "not_selected"
    SELECTED = "selected"
    EDGE = "edge"


initial_times_statuses = [ScheduleTimeStatus.NOT_SELECTED] * TIMES_STATUSES_LEN


def _no_isolated_selected(times_statuses: list[str]) -> bool:
    assert len(times_statuses) >= MINIMAL_TIMES_STATUSES_LEN
    if (
        times_statuses[0] == ScheduleTimeStatus.SELECTED
        and times_statuses[1] != ScheduleTimeStatus.SELECTED
    ) or (
        times_statuses[-1] == ScheduleTimeStatus.SELECTED
        and times_statuses[-2] != ScheduleTimeStatus.SELECTED
    ):
        return False
    for i in range(1, len(times_statuses) - 1):
        if (
            times_statuses[i] == ScheduleTimeStatus.SELECTED
            and times_statuses[i-1] != ScheduleTimeStatus.SELECTED
            and times_statuses[i+1] != ScheduleTimeStatus.SELECTED
        ):
            return False
    return True


def _no_edge_selected_combination(times_statuses: list[str]) -> bool:
    assert len(times_statuses) >= MINIMAL_TIMES_STATUSES_LEN
    for i in range(len(times_statuses) - 1):
        if (
            times_statuses[i] == ScheduleTimeStatus.EDGE
            and times_statuses[i+1] == ScheduleTimeStatus.SELECTED
        ):
            return False
    return True


def _no_selected_edge_combination(times_statuses: list[str]) -> bool:
    assert len(times_statuses) >= MINIMAL_TIMES_STATUSES_LEN
    for i in range(len(times_statuses) - 1):
        if (
            times_statuses[i] == ScheduleTimeStatus.SELECTED
            and times_statuses[i+1] == ScheduleTimeStatus.EDGE
        ):
            return False
    return True


def check_times_statuses_assertions(times_statuses: list[str]) -> None:
    """
    Проверка отсутствия невозможных сценариев для times_status.

    При наличии невозможного сценария вызывается AssertionError.
    """
    possible_statuses = [
        ScheduleTimeStatus.SELECTED,
        ScheduleTimeStatus.NOT_SELECTED,
        ScheduleTimeStatus.EDGE,
    ]
    assert len(times_statuses) == TIMES_STATUSES_LEN
    assert all([status in possible_statuses for status in times_statuses])
    assert times_statuses.count(ScheduleTimeStatus.EDGE) <= 1
    assert _no_isolated_selected(times_statuses)
    assert _no_edge_selected_combination(times_statuses)
    assert _no_selected_edge_combination(times_statuses)


def check_clicked_index_assertions(clicked_index: int) -> None:
    """
    Проверка отсутствия невозможных сценариев для clicked_index.

    При наличии невозможного сценария вызывается AssertionError.
    """
    assert clicked_index in range(TIMES_STATUSES_LEN)


def _get_duration_multiplier_by_times_statues(times_statuses_len: int) -> int:
    assert times_statuses_len >= MINIMAL_TIMES_STATUSES_LEN
    duration_multiplier = 24*60/(times_statuses_len - 1)
    return int(duration_multiplier)


def _get_iso_time_from_time_index(index: int, duration_multiplier: int) -> str:
    total_minutes = index * duration_multiplier
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    time_ = time(hours, minutes)
    return time_.isoformat(timespec="minutes")


def get_times_statuses_view(times_statuses: list[str]) -> str:
    view = ""
    duration_multiplier = _get_duration_multiplier_by_times_statues(len(times_statuses))
    prev_element = None
    for i in range(len(times_statuses)):
        current_element = times_statuses[i]
        try:
            next_element = times_statuses[i+1]
        except IndexError:
            next_element = None
        iso_time = _get_iso_time_from_time_index(i, duration_multiplier)
        if current_element == ScheduleTimeStatus.EDGE:
            view += "\n"
            if prev_element:
                view += "...-"
            view += iso_time
            if next_element:
                view += "-..."
        elif current_element == ScheduleTimeStatus.SELECTED:
            if prev_element != ScheduleTimeStatus.SELECTED:
                view += f"\n{iso_time}-"
            elif next_element != ScheduleTimeStatus.SELECTED:
                view += f"{iso_time}"
        prev_element = times_statuses[i]
    view = view.strip()
    if view == "":
        view = "Рабочие часы не выбраны"
    else:
        view = "Выбранные рабочие часы:\n" + view
    return view


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


def get_set_working_hours_keyboard_buttons(times_statuses: list[str]) -> list[InlineButton]:
    result = []
    for i in range(len(times_statuses)):
        iso_time = _get_iso_time_from_time_index(i, DURATION_MULTIPLIER)
        if times_statuses[i] == ScheduleTimeStatus.EDGE:
            text = "⚪️"
        elif times_statuses[i] == ScheduleTimeStatus.SELECTED:
            text = "✔️"
        else:
            text = iso_time
        result.append(InlineButton("time_clicked", text, value=str(i)))
    return result
