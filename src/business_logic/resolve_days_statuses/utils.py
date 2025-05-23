import re
from calendar import Calendar
from datetime import date, datetime, timedelta

from src import messages
from src.keyboards import InlineButton
from src.utils import months


MIN_DAYS_STATUSES_LEN = 40


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
