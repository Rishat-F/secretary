from datetime import datetime

import pytest

from src.stuff.appointments.exceptions import (
    DayBecomeNotAvailable,
    MonthBecomeNotAvailable,
    TimeBecomeNotAvailable,
    YearBecomeNotAvailable,
)
from src.stuff.appointments.keyboards import InlineButton
from src.stuff.appointments.utils import (
    check_chosen_datetime_is_possible,
    get_datetimes_needed_for_appointment,
    get_times_for_appointment,
    get_months_keyboard_buttons,
    get_years_keyboard_buttons,
)


@pytest.mark.parametrize(
    "datetime_,slots,expected_exception,expected_exception_message",
    [
        (
            datetime(2026, 6, 15),
            {2027: {3: {18: ["10:00"]}}},
            YearBecomeNotAvailable,
            "2026 год стал недоступен для записи",
        ),
        (
            datetime(2026, 6, 15),
            {2026: {3: {18: ["10:00"]}}},
            MonthBecomeNotAvailable,
            "Июнь 2026 года стал недоступен для записи",
        ),
        (
            datetime(2026, 6, 15),
            {2026: {6: {18: ["10:00"]}}},
            DayBecomeNotAvailable,
            "15 июня 2026 года стало недоступно для записи",
        ),
        (
            datetime(2026, 6, 15, 9, 0),
            {2026: {6: {15: ["10:00"]}}},
            TimeBecomeNotAvailable,
            "Время 09:00 стало недоступно для записи",
        ),
    ],
)
def test_check_chosen_datetime_is_possible_raise_exception(
    datetime_,
    slots,
    expected_exception,
    expected_exception_message,
):
    with pytest.raises(expected_exception, match=expected_exception_message):
        check_chosen_datetime_is_possible(datetime_, slots)


def test_check_chosen_datetime_is_possible_not_raise_exception():
    assert check_chosen_datetime_is_possible(
        datetime(2026, 6, 15, 9, 0),
        {2026: {6: {15: ["09:00"]}}},
    ) is None


@pytest.mark.parametrize(
    "starts_at,duration,expected_datetimes",
    [
        (
            datetime(2020, 1, 1, 10, 0),
            30,
            [datetime(2020, 1, 1, 10, 0)],
        ),
        (
            datetime(2020, 1, 1, 10, 0),
            60,
            [datetime(2020, 1, 1, 10, 0), datetime(2020, 1, 1, 10, 30)],
        ),
        (
            datetime(2020, 1, 1, 10, 0),
            90,
            [
                datetime(2020, 1, 1, 10, 0),
                datetime(2020, 1, 1, 10, 30),
                datetime(2020, 1, 1, 11, 0),
            ],
        ),
        (
            datetime(2020, 1, 1, 10, 0),
            120,
            [
                datetime(2020, 1, 1, 10, 0),
                datetime(2020, 1, 1, 10, 30),
                datetime(2020, 1, 1, 11, 0),
                datetime(2020, 1, 1, 11, 30),
            ],
        ),
    ],
)
def test_get_datetimes_needed_for_appointment(starts_at, duration, expected_datetimes):
    assert get_datetimes_needed_for_appointment(starts_at, duration) == expected_datetimes


@pytest.mark.parametrize(
    "years_with_months,current_year,current_month,chosen_year,expected_result",
    [
        (
            {
                2025: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                2026: [2, 4, 7, 11],
                2027: [6, 7, 8, 9],
                2028: [11],
            },
            2024,
            4,
            2025,
            [
                InlineButton("choose_day", "Январь", 1),
                InlineButton("choose_day", "Февраль", 2),
                InlineButton("choose_day", "Март", 3),
                InlineButton("choose_day", "Апрель", 4),
                InlineButton("choose_day", "Май", 5),
                InlineButton("choose_day", "Июнь", 6),
                InlineButton("choose_day", "Июль", 7),
                InlineButton("choose_day", "Август", 8),
                InlineButton("choose_day", "Сентябрь", 9),
                InlineButton("choose_day", "Октябрь", 10),
                InlineButton("choose_day", "Ноябрь", 11),
                InlineButton("choose_day", "Декабрь", 12),
            ],
        ),
        (
            {
                2025: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                2026: [2, 4, 7, 11],
                2027: [6, 7, 8, 9],
                2028: [11],
            },
            2025,
            4,
            2025,
            [
                InlineButton("ignore", " ", 1),
                InlineButton("ignore", " ", 2),
                InlineButton("ignore", " ", 3),
                InlineButton("choose_day", "[ Апрель ]", 4),
                InlineButton("choose_day", "Май", 5),
                InlineButton("choose_day", "Июнь", 6),
                InlineButton("choose_day", "Июль", 7),
                InlineButton("choose_day", "Август", 8),
                InlineButton("choose_day", "Сентябрь", 9),
                InlineButton("choose_day", "Октябрь", 10),
                InlineButton("choose_day", "Ноябрь", 11),
                InlineButton("choose_day", "Декабрь", 12),
            ],
        ),
        (
            {
                2025: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                2026: [2, 4, 7, 11],
                2027: [6, 7, 8, 9],
                2028: [11],
            },
            2026,
            5,
            2026,
            [
                InlineButton("ignore", " ", 1),
                InlineButton("ignore", " ", 2),
                InlineButton("ignore", " ", 3),
                InlineButton("ignore", " ", 4),
                InlineButton("not_available", "[ ✖️ ]", 5),
                InlineButton("not_available", "✖️", 6),
                InlineButton("choose_day", "Июль", 7),
                InlineButton("not_available", "✖️", 8),
                InlineButton("not_available", "✖️", 9),
                InlineButton("not_available", "✖️", 10),
                InlineButton("choose_day", "Ноябрь", 11),
                InlineButton("not_available", "✖️", 12),
            ],
        ),
        (
            {
                2025: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                2026: [2, 4, 7, 11],
                2027: [6, 7, 8, 9],
                2028: [11],
            },
            2027,
            3,
            2027,
            [
                InlineButton("ignore", " ", 1),
                InlineButton("ignore", " ", 2),
                InlineButton("not_available", "[ ✖️ ]", 3),
                InlineButton("not_available", "✖️", 4),
                InlineButton("not_available", "✖️", 5),
                InlineButton("choose_day", "Июнь", 6),
                InlineButton("choose_day", "Июль", 7),
                InlineButton("choose_day", "Август", 8),
                InlineButton("choose_day", "Сентябрь", 9),
                InlineButton("not_available", "✖️", 10),
                InlineButton("not_available", "✖️", 11),
                InlineButton("not_available", "✖️", 12),
            ],
        ),
        (
            {
                2025: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                2026: [2, 4, 7, 11],
                2027: [6, 7, 8, 9],
                2028: [11],
            },
            2027,
            3,
            2028,
            [
                InlineButton("not_available", "✖️", 1),
                InlineButton("not_available", "✖️", 2),
                InlineButton("not_available", "✖️", 3),
                InlineButton("not_available", "✖️", 4),
                InlineButton("not_available", "✖️", 5),
                InlineButton("not_available", "✖️", 6),
                InlineButton("not_available", "✖️", 7),
                InlineButton("not_available", "✖️", 8),
                InlineButton("not_available", "✖️", 9),
                InlineButton("not_available", "✖️", 10),
                InlineButton("choose_day", "Ноябрь", 11),
                InlineButton("not_available", "✖️", 12),
            ],
        ),
    ],
)
def test_get_months_keyboard_buttons(
    years_with_months,
    current_year,
    current_month,
    chosen_year,
    expected_result,
):
    now_ = datetime(current_year, current_month, 15)
    result = get_months_keyboard_buttons(years_with_months, now_, chosen_year)
    assert result == expected_result


@pytest.mark.parametrize(
    "slots_datetimes,service_duration,expected_possible_times",
    [
        ([], 30, []),
        ([], 90, []),
        ([datetime(2000, 1, 1, 10, 0)], 30, ["10:00"]),
        ([datetime(2000, 1, 1, 10, 0)], 60, []),
        (
            [datetime(2000, 1, 1, 10, 0), datetime(2000, 1, 1, 10, 30)],
            60,
            ["10:00"],
        ),
        (
            [
                datetime(2000, 1, 1, 10, 0),
                datetime(2000, 1, 1, 10, 30),
                datetime(2000, 1, 1, 11, 0),
            ],
            60,
            ["10:00", "10:30"],
        ),
        (
            [
                datetime(2000, 1, 1, 10, 0),
                datetime(2000, 1, 1, 10, 30),
                datetime(2000, 1, 1, 11, 0),
            ],
            30,
            ["10:00", "10:30", "11:00"],
        ),
        (
            [
                datetime(2000, 1, 1, 10, 0),
                datetime(2000, 1, 1, 10, 30),
                datetime(2000, 1, 1, 11, 0),
            ],
            90,
            ["10:00"],
        ),
        (
            [
                datetime(2000, 1, 1, 10, 0),
                datetime(2000, 1, 1, 10, 30),
                datetime(2000, 1, 2, 11, 0),
            ],
            90,
            [],
        ),
        (
            [
                datetime(2000, 1, 1, 10, 0),
                datetime(2000, 1, 1, 10, 30),
                datetime(2000, 1, 1, 11, 0),
            ],
            120,
            [],
        ),
        (
            [
                datetime(2000, 1, 1, 10, 0),
                datetime(2000, 1, 1, 15, 0),
                datetime(2000, 1, 1, 20, 0),
            ],
            30,
            ["10:00", "15:00", "20:00"],
        ),
        (
            [
                datetime(2000, 1, 1, 10, 0),
                datetime(2000, 1, 1, 15, 0),
            ],
            60,
            [],
        ),
        (
            [
                datetime(2000, 1, 1, 10, 0),
                datetime(2000, 1, 1, 15, 0),
                datetime(2000, 1, 1, 15, 30),
                datetime(2000, 1, 1, 16, 0),
                datetime(2000, 1, 1, 20, 0),
                datetime(2000, 1, 1, 20, 30),
            ],
            60,
            ["15:00", "15:30", "20:00"],
        ),
        (
            [
                datetime(2000, 1, 1, 23, 0),
                datetime(2000, 1, 1, 23, 30),
                datetime(2000, 1, 2, 0, 0),
                datetime(2000, 1, 2, 0, 30),
            ],
            60,
            ["23:00", "23:30", "00:00"],
        ),
    ],
)
def test_get_times_for_appointment(slots_datetimes, service_duration, expected_possible_times):
    assert get_times_for_appointment(slots_datetimes, service_duration) == expected_possible_times


@pytest.mark.parametrize(
    "years,current_year,expected_result",
    [
        ([], 2025, []),
        ([2025], 2026, []),
        (
            [2025],
            2025,
            [
                InlineButton("choose_month", "[ 2025 ]", 2025),
            ],
        ),
        (
            [2025],
            2024,
            [
                InlineButton("not_available", "[ ✖️ ]", 2024),
                InlineButton("choose_month", "2025", 2025),
            ],
        ),
        (
            [2025, 2026],
            2024,
            [
                InlineButton("not_available", "[ ✖️ ]", 2024),
                InlineButton("choose_month", "2025", 2025),
            ],
        ),
        (
            [2025, 2026],
            2025,
            [
                InlineButton("choose_month", "[ 2025 ]", 2025),
                InlineButton("choose_month", "2026", 2026),
            ],
        ),
        (
            [2025, 2026],
            2026,
            [
                InlineButton("choose_month", "[ 2026 ]", 2026),
            ],
        ),
        (
            [2025, 2026],
            2027,
            [],
        ),
        (
            [2024, 2026, 2027],
            2023,
            [
                InlineButton("not_available", "[ ✖️ ]", 2023),
                InlineButton("choose_month", "2024", 2024),
            ],
        ),
        (
            [2024, 2026, 2027],
            2024,
            [
                InlineButton("choose_month", "[ 2024 ]", 2024),
            ],
        ),
        (
            [2024, 2026, 2027],
            2025,
            [
                InlineButton("not_available", "[ ✖️ ]", 2025),
                InlineButton("choose_month", "2026", 2026),
            ],
        ),
        (
            [2024, 2026, 2027],
            2026,
            [
                InlineButton("choose_month", "[ 2026 ]", 2026),
                InlineButton("choose_month", "2027", 2027),
            ],
        ),
        (
            [2024, 2026, 2027],
            2027,
            [
                InlineButton("choose_month", "[ 2027 ]", 2027),
            ],
        ),
        (
            [2024, 2026, 2027],
            2020,
            [
                InlineButton("not_available", "[ ✖️ ]", 2020),
                InlineButton("not_available", "✖️", 2021),
                InlineButton("not_available", "✖️", 2022),
                InlineButton("not_available", "✖️", 2023),
                InlineButton("choose_month", "2024", 2024),
            ],
        ),
    ],
)
def test_get_years_keyboard_buttons(years, current_year, expected_result):
    now_ = datetime(current_year, 6, 15)
    result = get_years_keyboard_buttons(years, now_)
    assert result == expected_result
