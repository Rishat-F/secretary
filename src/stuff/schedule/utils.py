import re
from calendar import Calendar
from datetime import date, datetime, time, timedelta

from src import messages
from src.config import TIMEZONE
from src.constraints import DURATION_MULTIPLIER
from src.models import Slot
from src.stuff.common.keyboards import InlineButton
from src.stuff.common.utils import from_utc, months, to_utc


def get_all_times_len(duration_multiplier: int) -> int:
    all_times_len = (24 * 60) // duration_multiplier + 1
    return all_times_len


MIN_DAYS_STATUSES_LEN = 40
TIMES_STATUSES_LEN = get_all_times_len(DURATION_MULTIPLIER)
MINIMAL_ALL_TIMES_LEN = 3
MINIMAL_TIMES_STATUSES_LEN = MINIMAL_ALL_TIMES_LEN


class ScheduleDayStatus:
    NOT_AVAILABLE = "not_available_"
    NOT_SELECTED = "not_selected_"
    SELECTED = "selected_"
    IGNORE = "ignore"


class ScheduleDayGroup:
    ALL = "all"
    WEEK1 = "week1"
    WEEK2 = "week2"
    WEEK3 = "week3"
    WEEK4 = "week4"
    WEEK5 = "week5"
    WEEK6 = "week6"
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class ScheduleTimeStatus:
    NOT_SELECTED = "not_selected"
    SELECTED = "selected"
    EDGE = "edge"


def get_schedule(
    slots: list[Slot],
) -> dict[int, dict[int, dict[int, list[str]]]]:
    """
    Получение графика работы.

    Возвращается словарь вида:
    {
        2024: {
            12: {
                29: ["10:00", "10:30", "14:30"],
                30: ["08:30", "11:00", "19:00", "19:30"],
            },
        2025: {
            2: {
                26: ["10:00", "10:30", "14:30"],
                27: ["08:30", "11:00", "19:00", "19:30],
                28: ["16:00"],
            },
            3: {
                1: ["10:00", "10:30", "14:30"],
                2: ["08:30", "11:00", "19:00", "19:30],
                3: ["16:00"],
            },
        },
    }
    """
    slots_dict = {}
    for slot in slots:
        slot_tz_datetime = from_utc(slot.datetime_, TIMEZONE)
        if slot_tz_datetime.year not in slots_dict:
            slots_dict[slot_tz_datetime.year] = {}
        if slot_tz_datetime.month not in slots_dict[slot_tz_datetime.year]:
            slots_dict[slot_tz_datetime.year][slot_tz_datetime.month] = {}
        if slot_tz_datetime.day not in slots_dict[slot_tz_datetime.year][slot_tz_datetime.month]:
            slots_dict[slot_tz_datetime.year][slot_tz_datetime.month][slot_tz_datetime.day] = []
        slots_dict[slot_tz_datetime.year][slot_tz_datetime.month][slot_tz_datetime.day].append(slot_tz_datetime)
    times_dict = {}
    for year_ in slots_dict:
        for month_ in slots_dict[year_]:
            for day_ in slots_dict[year_][month_]:
                slots_datetimes_ = slots_dict[year_][month_][day_]
                times = get_schedule_times(slots_datetimes_)
                if year_ not in times_dict:
                    times_dict[year_] = {}
                if month_ not in times_dict[year_]:
                    times_dict[year_][month_] = {}
                if day_ not in times_dict[year_][month_]:
                    times_dict[year_][month_][day_] = times
    return times_dict


def _get_groups_possible_elements() -> list[str]:
    groups_possible_elements = []
    for status in [
        ScheduleDayStatus.NOT_AVAILABLE,
        ScheduleDayStatus.SELECTED,
        ScheduleDayStatus.NOT_SELECTED,
    ]:
        for group in [
            ScheduleDayGroup.WEEK1,
            ScheduleDayGroup.WEEK2,
            ScheduleDayGroup.WEEK3,
            ScheduleDayGroup.WEEK4,
            ScheduleDayGroup.WEEK5,
            ScheduleDayGroup.WEEK6,
            ScheduleDayGroup.MONDAY,
            ScheduleDayGroup.TUESDAY,
            ScheduleDayGroup.WEDNESDAY,
            ScheduleDayGroup.THURSDAY,
            ScheduleDayGroup.FRIDAY,
            ScheduleDayGroup.SATURDAY,
            ScheduleDayGroup.SUNDAY,
        ]:
            groups_possible_elements.append(f"{status}{group}")
    groups_possible_elements.append(f"{ScheduleDayStatus.SELECTED}{ScheduleDayGroup.ALL}")
    groups_possible_elements.append(f"{ScheduleDayStatus.NOT_SELECTED}{ScheduleDayGroup.ALL}")
    return groups_possible_elements


groups_possible_elements = tuple(_get_groups_possible_elements())


def _is_element_valid(element: str) -> bool:
    day_element_pattern = (
        rf"(?:{ScheduleDayStatus.NOT_AVAILABLE}|{ScheduleDayStatus.NOT_SELECTED}|{ScheduleDayStatus.SELECTED})"
        r"\d\d\d\d-\d\d-\d\d"
    )
    return (
        element in groups_possible_elements
        or element == ScheduleDayStatus.IGNORE
        or bool(re.fullmatch(day_element_pattern, element))
    )


def _is_day_element(element: str) -> bool:
    pattern = r"_\d\d\d\d-\d\d-\d\d$"
    return bool(re.search(pattern, element))


def is_week_element(element: str) -> bool:
    return "week" in element


def is_day_of_week_element(element: str) -> bool:
    return any(
        [
            ScheduleDayGroup.MONDAY in element,
            ScheduleDayGroup.TUESDAY in element,
            ScheduleDayGroup.WEDNESDAY in element,
            ScheduleDayGroup.THURSDAY in element,
            ScheduleDayGroup.FRIDAY in element,
            ScheduleDayGroup.SATURDAY in element,
            ScheduleDayGroup.SUNDAY in element,
        ]
    )


def _at_least_one_available_day(days_statuses) -> bool:
    for element in days_statuses:
        if (
            _is_day_element(element)
            and (
                ScheduleDayStatus.NOT_SELECTED in element
                or ScheduleDayStatus.SELECTED in element
            )
        ):
            return True
    return False


def _no_not_available_day_after_available(days_statuses) -> bool:
    days_elements = [element for element in days_statuses if _is_day_element(element)]
    prev_element = ""
    for element in days_elements:
        if (
            (
                ScheduleDayStatus.NOT_SELECTED in prev_element
                or ScheduleDayStatus.SELECTED in prev_element
            )
            and ScheduleDayStatus.NOT_AVAILABLE in element
        ):
            return False
        prev_element = element
    return True


def _at_least_one_available_week(days_statuses) -> bool:
    for element in days_statuses:
        if (
            is_week_element(element)
            and (
                ScheduleDayStatus.NOT_SELECTED in element
                or ScheduleDayStatus.SELECTED in element
            )
        ):
            return True
    return False


def _no_not_available_week_after_available(days_statuses) -> bool:
    weeks_elements = [element for element in days_statuses if is_week_element(element)]
    prev_element = ""
    for element in weeks_elements:
        if (
            (
                ScheduleDayStatus.NOT_SELECTED in prev_element
                or ScheduleDayStatus.SELECTED in prev_element
            )
            and ScheduleDayStatus.NOT_AVAILABLE in element
        ):
            return False
        prev_element = element
    return True


def _at_least_one_available_day_of_week(days_statuses) -> bool:
    for element in days_statuses:
        if (
            is_day_of_week_element(element)
            and (
                ScheduleDayStatus.NOT_SELECTED in element
                or ScheduleDayStatus.SELECTED in element
            )
        ):
            return True
    return False


def _uniform_ascending_days(days_elements: list[str]) -> bool:
    iso_dates = [
        element.rsplit(sep="_", maxsplit=1)[-1] for element in days_elements
    ]
    for i in range(1, len(iso_dates)):
        prev_element = date.fromisoformat(iso_dates[i-1])
        current_element = date.fromisoformat(iso_dates[i])
        if current_element - prev_element != timedelta(days=1):
            return False
    return True


def _uniform_ascending_weeks(weeks_elements: list[str]) -> bool:
    weeks = [int(element[-1]) for element in weeks_elements]
    for i in range(1, len(weeks)):
        if weeks[i] - weeks[i-1] != 1:
            return False
    return True


def _uniform_ascending_elements(days_statuses: list[str]) -> bool:
    days_elements = []
    weeks_elements = []
    for element in days_statuses:
        if _is_day_element(element):
            days_elements.append(element)
        elif is_week_element(element):
            weeks_elements.append(element)
    return _uniform_ascending_days(days_elements) and _uniform_ascending_weeks(weeks_elements)


def _elements_in_right_place(days_statuses: list[str]) -> bool:
    for i in range(len(days_statuses)):
        element = days_statuses[i]
        if i == 0:
            if ScheduleDayGroup.ALL not in element:
                return False
        elif i == 1:
            if ScheduleDayGroup.MONDAY not in element:
                return False
        elif i == 2:
            if ScheduleDayGroup.TUESDAY not in element:
                return False
        elif i == 3:
            if ScheduleDayGroup.WEDNESDAY not in element:
                return False
        elif i == 4:
            if ScheduleDayGroup.THURSDAY not in element:
                return False
        elif i == 5:
            if ScheduleDayGroup.FRIDAY not in element:
                return False
        elif i == 6:
            if ScheduleDayGroup.SATURDAY not in element:
                return False
        elif i == 7:
            if ScheduleDayGroup.SUNDAY not in element:
                return False
        elif i % 8 == 0:
            if not is_week_element(element):
                return False
        else:
            if not (_is_day_element(element) or element == ScheduleDayStatus.IGNORE):
                return False
    return True


def _no_ignore_element_among_days_elements(days_statuses: list[str]) -> bool:
    ignore_elements_indexes = []
    days_elements_indexes = []
    for i in range(len(days_statuses)):
        if days_statuses[i] == ScheduleDayStatus.IGNORE:
            ignore_elements_indexes.append(i)
        elif _is_day_element(days_statuses[i]):
            days_elements_indexes.append(i)
    for ignore_index in ignore_elements_indexes:
        days_before_exist = False
        days_after_exist = False
        for day_index in days_elements_indexes:
            if day_index < ignore_index:
                days_before_exist = True
            elif day_index > ignore_index:
                days_after_exist = True
            if days_before_exist and days_after_exist:
                return False
    return True


def _at_least_one_should_be_selected(elements: list[str]) -> bool:
    for element in elements:
        element_status, _ = split_element(element)
        if element_status == ScheduleDayStatus.SELECTED:
            return True
    return False


def _at_least_one_should_be_not_selected(elements: list[str]) -> bool:
    for element in elements:
        element_status, _ = split_element(element)
        if element_status == ScheduleDayStatus.NOT_SELECTED:
            return True
    return False


def _noone_should_be_selected(elements: list[str]) -> bool:
    for element in elements:
        element_status, _ = split_element(element)
        if element_status == ScheduleDayStatus.SELECTED:
            return False
    return True


def _all_days_should_be_not_available_or_ignore(days_elements: list[str]) -> bool:
    for element in days_elements:
        element_status, _ = split_element(element)
        if not (
            element_status == ScheduleDayStatus.NOT_AVAILABLE
            or element_status == ScheduleDayStatus.IGNORE
        ):
            return False
    return True


def _all_group_selected_right(days_statuses: list[str]) -> bool:
    days_elements = []
    weeks_elements = []
    day_of_week_elements = []
    for element in days_statuses:
        if _is_day_element(element):
            days_elements.append(element)
        elif is_week_element(element):
            weeks_elements.append(element)
        elif is_day_of_week_element(element):
            day_of_week_elements.append(element)
    all_group_status, _ = split_element(days_statuses[0])
    if all_group_status == ScheduleDayStatus.SELECTED:
        return (
            _at_least_one_should_be_selected(days_elements)
            and _at_least_one_should_be_selected(weeks_elements)
            and _at_least_one_should_be_selected(day_of_week_elements)
        )
    else:
        return (
            _noone_should_be_selected(days_elements)
            and _noone_should_be_selected(weeks_elements)
            and _noone_should_be_selected(day_of_week_elements)
        )


def _no_week_with_all_days_ignore(days_statuses: list[str]) -> bool:
    for i in range(8, len(days_statuses), 8):
        days_elements = days_statuses[i+1:i+8]
        for element in days_elements:
            element_status, _ = split_element(element)
            if element_status != ScheduleDayStatus.IGNORE:
                return True
    return False


def _is_group_status_right(group_status: str, group_days_elements: list[str]) -> bool:
    if group_status == ScheduleDayStatus.SELECTED:
        if not _at_least_one_should_be_selected(group_days_elements):
            return False
    elif group_status == ScheduleDayStatus.NOT_SELECTED:
        if not (
            _noone_should_be_selected(group_days_elements)
            and _at_least_one_should_be_not_selected(group_days_elements)
        ):
            return False
    else:
        if not _all_days_should_be_not_available_or_ignore(group_days_elements):
            return False
    return True


def _weeks_groups_statuses_right(days_statuses: list[str]) -> bool:
    for i in range(8, len(days_statuses), 8):
        days_elements = days_statuses[i+1:i+8]
        week_group_status, _ = split_element(days_statuses[i])
        if not _is_group_status_right(week_group_status, days_elements):
            return False
    return True


def _all_ignore(elements: list[str]) -> bool:
    for element in elements:
        if element != ScheduleDayStatus.IGNORE:
            return False
    return True


def _collect_days_of_week(days_statuses: list[str]) -> dict[str, dict[str, list[str] | str]]:
    collected_days_of_week = {}
    for i in range(1, 8):
        day_of_week_group_element = days_statuses[i]
        day_of_week_group_status, day_of_week = split_element(day_of_week_group_element)
        collected_days_of_week[day_of_week] = {}
        collected_days_of_week[day_of_week]["status"] = day_of_week_group_status
        collected_days_of_week[day_of_week]["days_elements"] = []
    for i in range(8, len(days_statuses)):
        element = days_statuses[i]
        if i % 8 == 1:
            collected_days_of_week[ScheduleDayGroup.MONDAY]["days_elements"].append(element)
        elif i % 8 == 2:
            collected_days_of_week[ScheduleDayGroup.TUESDAY]["days_elements"].append(element)
        elif i % 8 == 3:
            collected_days_of_week[ScheduleDayGroup.WEDNESDAY]["days_elements"].append(element)
        elif i % 8 == 4:
            collected_days_of_week[ScheduleDayGroup.THURSDAY]["days_elements"].append(element)
        elif i % 8 == 5:
            collected_days_of_week[ScheduleDayGroup.FRIDAY]["days_elements"].append(element)
        elif i % 8 == 6:
            collected_days_of_week[ScheduleDayGroup.SATURDAY]["days_elements"].append(element)
        elif i % 8 == 7:
            collected_days_of_week[ScheduleDayGroup.SUNDAY]["days_elements"].append(element)
    return collected_days_of_week


def _no_day_of_week_with_all_days_ignore(days_statuses: list[str]) -> bool:
    collected_days_of_week = _collect_days_of_week(days_statuses)
    for item in collected_days_of_week.values():
        days_elements = item["days_elements"]
        assert isinstance(days_elements, list)
        if _all_ignore(days_elements):
            return False
    return True


def _day_of_week_groups_statuses_right(days_statuses: list[str]) -> bool:
    collected_days_of_week = _collect_days_of_week(days_statuses)
    for dict_ in collected_days_of_week.values():
        day_of_week_group_status = dict_["status"]
        day_of_week_days_elements = dict_["days_elements"]
        assert isinstance(day_of_week_group_status, str)
        assert isinstance(day_of_week_days_elements, list)
        if not _is_group_status_right(day_of_week_group_status, day_of_week_days_elements):
            return False
    return True


def check_days_statuses_assertions(days_statuses: list[str]) -> None:
    """
    Проверка отсутствия невозможных сценариев для days_statuses.

    При наличии невозможного сценария вызывается AssertionError.
    """
    assert len(days_statuses) >= MIN_DAYS_STATUSES_LEN
    assert (len(days_statuses) % 8) == 0
    for element in days_statuses:
        assert _is_element_valid(element)
    assert _at_least_one_available_day(days_statuses)
    assert _no_not_available_day_after_available(days_statuses)
    assert _at_least_one_available_week(days_statuses)
    assert _no_not_available_week_after_available(days_statuses)
    assert _at_least_one_available_day_of_week(days_statuses)
    assert _uniform_ascending_elements(days_statuses)
    assert _elements_in_right_place(days_statuses)
    assert _no_ignore_element_among_days_elements(days_statuses)
    assert _all_group_selected_right(days_statuses)
    assert _no_week_with_all_days_ignore(days_statuses)
    assert _weeks_groups_statuses_right(days_statuses)
    assert _no_day_of_week_with_all_days_ignore(days_statuses)
    assert _day_of_week_groups_statuses_right(days_statuses)


def check_clicked_element_assertions(clicked_element: str, days_statuses: list[str]) -> None:
    """
    Проверка отсутствия невозможных сценариев для clicked_element.

    При наличии невозможного сценария вызывается AssertionError.
    """
    assert _is_element_valid(clicked_element)
    clicked_element_status, _ = split_element(clicked_element)
    assert clicked_element_status not in [ScheduleDayStatus.NOT_AVAILABLE, ScheduleDayStatus.IGNORE]
    assert clicked_element in days_statuses


def split_element(element: str) -> tuple[str, str]:
    if ScheduleDayStatus.NOT_SELECTED in element:
        return ScheduleDayStatus.NOT_SELECTED, element.split(ScheduleDayStatus.NOT_SELECTED)[-1]
    elif ScheduleDayStatus.SELECTED in element:
        return ScheduleDayStatus.SELECTED, element.split(ScheduleDayStatus.SELECTED)[-1]
    elif ScheduleDayStatus.NOT_AVAILABLE in element:
        return ScheduleDayStatus.NOT_AVAILABLE, element.split(ScheduleDayStatus.NOT_AVAILABLE)[-1]
    else:
        return ScheduleDayStatus.IGNORE, ""


def change_all_days_selection_status(days_statuses: list[str], new_status: str) -> list[str]:
    for i in range(len(days_statuses)):
        if _is_day_element(days_statuses[i]):
            status, day = split_element(days_statuses[i])
            if status in [ScheduleDayStatus.NOT_SELECTED, ScheduleDayStatus.SELECTED]:
                days_statuses[i] = f"{new_status}{day}"
    return days_statuses


def change_day_of_week_days_selection_status(
    days_statuses: list[str],
    new_status: str,
    day_of_week_index: int,
) -> list[str]:
    for i in range(8, len(days_statuses)):
        if i % 8 == day_of_week_index:
            status, day = split_element(days_statuses[i])
            if status in [ScheduleDayStatus.NOT_SELECTED, ScheduleDayStatus.SELECTED]:
                days_statuses[i] = f"{new_status}{day}"
    return days_statuses


def change_week_days_selection_status(
    days_statuses: list[str],
    new_status: str,
    week_index: int,
) -> list[str]:
    for i in range(week_index + 1, week_index + 8):
        status, day = split_element(days_statuses[i])
        if status in [ScheduleDayStatus.NOT_SELECTED, ScheduleDayStatus.SELECTED]:
            days_statuses[i] = f"{new_status}{day}"
    return days_statuses


def actualize_groups_selection_status(days_statuses: list[str]) -> list[str]:
    selectable_days_elements = []
    for element in days_statuses:
        if _is_day_element(element):
            status, _ = split_element(element)
            if status in [ScheduleDayStatus.NOT_SELECTED, ScheduleDayStatus.SELECTED]:
                selectable_days_elements.append(element)
    if all(
        [ScheduleDayStatus.NOT_SELECTED in element for element in selectable_days_elements]
    ):
        actual_all_group_status = ScheduleDayStatus.NOT_SELECTED
    else:
        actual_all_group_status = ScheduleDayStatus.SELECTED
    days_statuses[0] = f"{actual_all_group_status}{ScheduleDayGroup.ALL}"

    for day_of_week_group_index in range(1, 8):
        _, day_of_week = split_element(days_statuses[day_of_week_group_index])
        day_of_week_selectable_days_elements = []
        for i in range(8, len(days_statuses)):
            element = days_statuses[i]
            if i % 8 == day_of_week_group_index:
                status, _ = split_element(element)
                if status in [ScheduleDayStatus.NOT_SELECTED, ScheduleDayStatus.SELECTED]:
                    day_of_week_selectable_days_elements.append(element)
        if not day_of_week_selectable_days_elements:
            actual_status = ScheduleDayStatus.NOT_AVAILABLE
        elif all(
            [ScheduleDayStatus.NOT_SELECTED in element for element in day_of_week_selectable_days_elements]
        ):
            actual_status = ScheduleDayStatus.NOT_SELECTED
        else:
            actual_status = ScheduleDayStatus.SELECTED
        days_statuses[day_of_week_group_index] = f"{actual_status}{day_of_week}"

    for week_group_index in range(8, len(days_statuses), 8):
        _, week = split_element(days_statuses[week_group_index])
        week_days_selectable_elements = []
        for element in days_statuses[week_group_index+1:week_group_index+8]:
            status, _ = split_element(element)
            if status in [ScheduleDayStatus.NOT_SELECTED, ScheduleDayStatus.SELECTED]:
                week_days_selectable_elements.append(element)
        if not week_days_selectable_elements:
            actual_status = ScheduleDayStatus.NOT_AVAILABLE
        elif all(
            [ScheduleDayStatus.NOT_SELECTED in element for element in week_days_selectable_elements]
        ):
            actual_status = ScheduleDayStatus.NOT_SELECTED
        else:
            actual_status = ScheduleDayStatus.SELECTED
        days_statuses[week_group_index] = f"{actual_status}{week}"

    check_days_statuses_assertions(days_statuses)
    return days_statuses


def get_selected_and_not_selected_dates(days_statuses: list[str]) -> tuple[list[str], list[str]]:
    selected_days: list[str] = []
    not_selected_days: list[str] = []
    for element in days_statuses:
        if _is_day_element(element):
            status, iso_date = split_element(element)
            if status == ScheduleDayStatus.SELECTED:
                selected_days.append(iso_date)
            elif status == ScheduleDayStatus.NOT_SELECTED:
                not_selected_days.append(iso_date)
    return selected_days, not_selected_days


def _get_years_months_days(iso_dates: list[str]) -> dict[int, dict[int, list[int]]]:
    iso_dates = sorted(iso_dates)
    years_months_days = {}
    for iso_date in iso_dates:
        date_ = date.fromisoformat(iso_date)
        if date_.year not in years_months_days:
            years_months_days[date_.year] = {}
        if date_.month not in years_months_days[date_.year]:
            years_months_days[date_.year][date_.month] = []
        years_months_days[date_.year][date_.month].append(date_.day)
    return years_months_days


def _get_month_selected_days_view(days: list[int]) -> str:
    view = ""
    prev_day = -1
    for i in range(len(days)):
        current_day = days[i]
        try:
            next_day = days[i+1]
        except IndexError:
            next_day = -1
        if current_day - prev_day != 1:
            view += f" {current_day}"
        else:
            if next_day - current_day != 1:
                view += f"-{current_day}"
        prev_day = current_day
    view = view.strip()
    view = view.replace(" ", ", ")
    return view


def get_selected_dates_view(iso_dates: list[str]) -> str:
    view = ""
    years_months_days = _get_years_months_days(iso_dates)
    for year in years_months_days:
        view += f"\n{str(year)}"
        for month in years_months_days[year]:
            view += f"\n      {months[month]}"
            month_selected_days_view = _get_month_selected_days_view(years_months_days[year][month])
            view += f"\n            {month_selected_days_view}"
    view = view.strip()
    if view == "":
        view = messages.SET_WORKING_DATES
    else:
        view = messages.SELECTED_WORKING_DATES.format(selected_dates_view=view)
    return view


def get_days_statuses(
    tz_now: datetime,
    selected_dates: list[str],
    chosen_year: int | None,
    chosen_month: int | None,
) -> list[str]:
    current_year = tz_now.year
    current_month = tz_now.month
    current_day = tz_now.day
    if chosen_year is None:
        assert chosen_month is None
        assert not selected_dates
        chosen_year = current_year
        chosen_month = current_month
    else:
        assert chosen_month is not None
    if chosen_year == current_year:
        assert chosen_month >= current_month
    days_statuses = [
        "not_selected_all",
        "not_selected_monday",
        "not_selected_tuesday",
        "not_selected_wednesday",
        "not_selected_thursday",
        "not_selected_friday",
        "not_selected_saturday",
        "not_selected_sunday",
    ]
    calendar = Calendar()
    week = 1
    for year, month, day, day_of_week_number in calendar.itermonthdays4(chosen_year, chosen_month):
        if month != chosen_month:
            element = ScheduleDayStatus.IGNORE
        else:
            iso_date = date(year, month, day).isoformat()
            if year == current_year and month == current_month:
                if day < current_day:
                    element = f"{ScheduleDayStatus.NOT_AVAILABLE}{iso_date}"
                else:
                    if iso_date in selected_dates:
                        element = f"{ScheduleDayStatus.SELECTED}{iso_date}"
                    else:
                        element = f"{ScheduleDayStatus.NOT_SELECTED}{iso_date}"
            else:
                if iso_date in selected_dates:
                    element = f"{ScheduleDayStatus.SELECTED}{iso_date}"
                else:
                    element = f"{ScheduleDayStatus.NOT_SELECTED}{iso_date}"
        days_statuses.append(element)
        if day_of_week_number % 7 == 6:
            week_element = f"{ScheduleDayStatus.NOT_AVAILABLE}week{week}"
            days_statuses.insert(week*8, week_element)
            week += 1
    days_statuses = actualize_groups_selection_status(days_statuses)
    return days_statuses


_days_of_week = {
    ScheduleDayGroup.MONDAY: "Пн",
    ScheduleDayGroup.TUESDAY: "Вт",
    ScheduleDayGroup.WEDNESDAY: "Ср",
    ScheduleDayGroup.THURSDAY: "Чт",
    ScheduleDayGroup.FRIDAY: "Пт",
    ScheduleDayGroup.SATURDAY: "Сб",
    ScheduleDayGroup.SUNDAY: "Вс",
}


def set_schedule_get_years_keyboard_buttons(now_: datetime) -> list[InlineButton]:
    result = []
    current_year = now_.year
    next_year = current_year + 1
    result.append(
        InlineButton(
            action="choose_month",
            text=f"[ {current_year} ]",
            value=str(current_year),
        ),
    )
    result.append(
        InlineButton(
            action="choose_month",
            text=f"{next_year}",
            value=str(next_year),
        ),
    )
    return result


def set_schedule_get_months_keyboard_buttons(
    now_: datetime,
    chosen_year: int,
) -> list[InlineButton]:
    current_year = now_.year
    current_month = now_.month
    assert chosen_year >= current_year
    result = []
    if chosen_year == current_year:
        for month_num, month_name in months.items():
            if month_num < current_month:
                result.append(InlineButton("not_available", "✖️", str(month_num)))
            elif month_num == current_month:
                result.append(InlineButton("choose_day", f"[ {month_name} ]", str(month_num)))
            else:
                result.append(InlineButton("choose_day", month_name, str(month_num)))
    else:
        for month_num, month_name in months.items():
            result.append(InlineButton("choose_day", month_name, str(month_num)))
    return result


def set_schedule_get_days_keyboard_buttons(days_statuses: list[str]) -> list[InlineButton]:
    result = []
    for i in range(len(days_statuses)):
        element = days_statuses[i]
        status, group_or_iso_date = split_element(element)
        if group_or_iso_date == ScheduleDayGroup.ALL:
            text = "↘️"
        elif is_day_of_week_element(element):
            text = _days_of_week[group_or_iso_date]
        elif is_week_element(element):
            text = "➞"
        else:
            if status == ScheduleDayStatus.IGNORE:
                text = " "
            elif status == ScheduleDayStatus.NOT_AVAILABLE:
                text = "✖️"
            elif status == ScheduleDayStatus.NOT_SELECTED:
                date_ = date.fromisoformat(group_or_iso_date)
                text = str(date_.day)
            else:
                text = "✔️"
        result.append(InlineButton(status, text, value=str(i)))
    return result


def resolve_days_statuses(days_statuses: list[str], clicked_element: str) -> list[str]:
    """Выбор диапазонов рабочих дней."""
    check_days_statuses_assertions(days_statuses)
    check_clicked_element_assertions(clicked_element, days_statuses)
    clicked_index = days_statuses.index(clicked_element)
    clicked_element_status, clicked_element_group_or_day = split_element(clicked_element)
    if clicked_element_status == ScheduleDayStatus.NOT_SELECTED:
        new_status = ScheduleDayStatus.SELECTED
    else:
        new_status = ScheduleDayStatus.NOT_SELECTED
    if clicked_element_group_or_day == ScheduleDayGroup.ALL:
        days_statuses = change_all_days_selection_status(days_statuses, new_status)
    elif is_day_of_week_element(clicked_element):
        days_statuses = change_day_of_week_days_selection_status(days_statuses, new_status, clicked_index)
    elif is_week_element(clicked_element):
        days_statuses = change_week_days_selection_status(days_statuses, new_status, clicked_index)
    else:
        _, day = split_element(clicked_element)
        days_statuses[clicked_index] = f"{new_status}{day}"
    days_statuses = actualize_groups_selection_status(days_statuses)
    return days_statuses


def get_initial_times_statuses() -> list[str]:
    statuses_times = [ScheduleTimeStatus.NOT_SELECTED] * TIMES_STATUSES_LEN
    return statuses_times


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
    Проверка отсутствия невозможных сценариев для times_statuses.

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


def _get_duration_multiplier_by_times_statuses(times_statuses_len: int) -> int:
    assert times_statuses_len >= MINIMAL_TIMES_STATUSES_LEN
    duration_multiplier = 24*60/(times_statuses_len - 1)
    return int(duration_multiplier)


def _get_iso_time_from_time_index(index: int, duration_multiplier: int) -> str:
    total_minutes = index * duration_multiplier
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    time_ = time(hours, minutes)
    return time_.isoformat(timespec="minutes")


def get_selected_times(times_statuses: list[str]) -> list[str]:
    selected_iso_times = []
    duration_multiplier = _get_duration_multiplier_by_times_statuses(len(times_statuses))
    for i in range(len(times_statuses)):
        current_element = times_statuses[i]
        try:
            next_element = times_statuses[i+1]
        except IndexError:
            next_element = None
        if (
            current_element == ScheduleTimeStatus.SELECTED
            and next_element == ScheduleTimeStatus.SELECTED
        ):
            iso_time = _get_iso_time_from_time_index(i, duration_multiplier)
            selected_iso_times.append(iso_time)
    return selected_iso_times


def get_times_statuses_view(times_statuses: list[str]) -> str:
    view = ""
    duration_multiplier = _get_duration_multiplier_by_times_statuses(len(times_statuses))
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
        view = messages.SET_WORKING_HOURS
    else:
        view = messages.SELECTED_WORKING_HOURS.format(selected_times_view=view)
    return view


def get_working_hours_view(iso_times: list[str], duration_multiplier: int) -> str:
    assert iso_times
    times = [time.fromisoformat(iso_time) for iso_time in iso_times]
    times = sorted(times)
    view = ""
    prev_element = None
    for i in range(len(times)):
        current_element = times[i]
        try:
            next_element = times[i+1]
        except IndexError:
            next_element = None
        if (
            prev_element is None
            or (
                (current_element.hour*60+current_element.minute) - (prev_element.hour*60+prev_element.minute)
            ) != duration_multiplier
        ):
            interval_start = current_element.isoformat(timespec="minutes")
            view += f"\n{interval_start}-"
        if (
            next_element is None
            or (
                (next_element.hour*60+next_element.minute) - (current_element.hour*60+current_element.minute)
            ) != duration_multiplier
        ):
            total_minutes = current_element.hour*60+current_element.minute
            interval_finish_minutes = total_minutes + duration_multiplier
            hours = (interval_finish_minutes // 60) % 24
            minutes = interval_finish_minutes % 60
            view += time(hours, minutes).isoformat(timespec="minutes")
        prev_element = times[i]
    view = view.strip()
    return view


def set_schedule_get_times_keyboard_buttons(times_statuses: list[str]) -> list[InlineButton]:
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


def get_slots_to_save(iso_tz_dates: list[str], iso_tz_times: list[str]) -> dict[str, list[str]]:
    assert iso_tz_dates
    assert iso_tz_times
    utc_slots: list[datetime] = []
    for iso_tz_date in iso_tz_dates:
        for iso_time in iso_tz_times:
            tz_date = date.fromisoformat(iso_tz_date)
            tz_time = time.fromisoformat(iso_time)
            slot_tz_dt = TIMEZONE.localize(datetime(tz_date.year, tz_date.month, tz_date.day, tz_time.hour, tz_time.minute))
            slot_utc_dt = to_utc(slot_tz_dt)
            utc_slots.append(slot_utc_dt)
    dates_slots = {}
    for utc_datetime in utc_slots:
        iso_date = utc_datetime.date().isoformat()
        iso_datetime = utc_datetime.replace(tzinfo=None).isoformat()
        if iso_date not in dates_slots:
            dates_slots[iso_date] = [iso_datetime]
        else:
            dates_slots[iso_date].append(iso_datetime)
    return dates_slots


def get_slots_to_delete(iso_tz_dates: list[str], iso_tz_times: list[str]) -> list[str]:
    assert iso_tz_dates
    assert iso_tz_times
    slots = []
    for iso_tz_date in iso_tz_dates:
        for iso_tz_time in iso_tz_times:
            tz_date = date.fromisoformat(iso_tz_date)
            tz_time = time.fromisoformat(iso_tz_time)
            slot_tz_dt = TIMEZONE.localize(datetime(tz_date.year, tz_date.month, tz_date.day, tz_time.hour, tz_time.minute))
            slot_utc_dt = to_utc(slot_tz_dt)
            iso_utc_datetime = slot_utc_dt.replace(tzinfo=None).isoformat()
            slots.append(iso_utc_datetime)
    return slots


def resolve_times_statuses(times_statuses: list[str], clicked_index: int) -> list[str]:
    """Выбор диапазонов рабочего времени."""
    check_times_statuses_assertions(times_statuses)
    check_clicked_index_assertions(clicked_index)
    prev_index = clicked_index - 1
    prev_prev_index = clicked_index - 2
    next_index = clicked_index + 1
    if ScheduleTimeStatus.EDGE in times_statuses:
        edge_index = times_statuses.index(ScheduleTimeStatus.EDGE)
        if clicked_index < edge_index:
            for i in range(clicked_index, edge_index + 1):
                times_statuses[i] = ScheduleTimeStatus.SELECTED
        elif clicked_index == edge_index:
            times_statuses[edge_index] = ScheduleTimeStatus.NOT_SELECTED
        else:
            for i in range(edge_index, next_index):
                times_statuses[i] = ScheduleTimeStatus.SELECTED
    else:
        if times_statuses[clicked_index] == ScheduleTimeStatus.NOT_SELECTED:
            try:
                prev_status = times_statuses[prev_index]
            except IndexError:
                prev_status = None
            try:
                next_status = times_statuses[next_index]
            except IndexError:
                next_status = None
            if (
                prev_status == ScheduleTimeStatus.SELECTED
                or next_status == ScheduleTimeStatus.SELECTED
            ):
                times_statuses[clicked_index] = ScheduleTimeStatus.SELECTED
            else:
                times_statuses[clicked_index] = ScheduleTimeStatus.EDGE
        else:
            if prev_prev_index < 0:
                prev_prev_status = None
            else:
                prev_prev_status = times_statuses[prev_prev_index]
            if prev_index < 0:
                prev_status = None
            else:
                prev_status = times_statuses[prev_index]
            if prev_status != ScheduleTimeStatus.SELECTED:
                for i in range(clicked_index, len(times_statuses)):
                    if times_statuses[i] != ScheduleTimeStatus.SELECTED:
                        break
                    times_statuses[i] = ScheduleTimeStatus.NOT_SELECTED
            else:
                for i in range(clicked_index, len(times_statuses)):
                    if times_statuses[i] != ScheduleTimeStatus.SELECTED:
                        break
                    times_statuses[i] = ScheduleTimeStatus.NOT_SELECTED
                if prev_prev_status != ScheduleTimeStatus.SELECTED:
                    times_statuses[prev_index] = ScheduleTimeStatus.EDGE
    check_times_statuses_assertions(times_statuses)
    return times_statuses


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
