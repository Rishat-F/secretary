from datetime import UTC, datetime, timedelta, timezone

import pytest
import pytz

from src.exceptions import (
    DayBecomeNotAvailable,
    MonthBecomeNotAvailable,
    TimeBecomeNotAvailable,
    YearBecomeNotAvailable,
)
from src.utils import (
    InlineButton,
    check_chosen_datetime_is_possible,
    date_to_lang,
    from_utc,
    get_datetimes_needed_for_appointment,
    get_months_keyboard_buttons,
    get_times_for_appointment,
    get_years_keyboard_buttons,
    get_years_with_months,
    get_years_with_months_days,
    to_utc,
    validate_service_duration,
)


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
    assert get_years_keyboard_buttons(years, now_) == expected_result


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
def test_get_months_keyboard_buttons(years_with_months, current_year, current_month, chosen_year, expected_result):
    now_ = datetime(current_year, current_month, 15)
    assert get_months_keyboard_buttons(years_with_months, now_, chosen_year) == expected_result


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
    "year,month,day,expected_result",
    [
        (2020, None, None, "2020 год"),
        (2020, 6, None, "Июнь 2020 года"),
        (2020, 6, 20, "20 июня 2020 года"),
        (2020, 3, 20, "20 марта 2020 года"),
    ],
)
def test_date_to_lang(year, month, day, expected_result):
    assert date_to_lang(year, month, day) == expected_result


@pytest.mark.parametrize(
    "slots,expected_result",
    [
        ({}, {}),
        (
            {
                2025: {3: {18: ["10:00"]}},
                2026: {
                    5: {
                        22: ["18:00", "18:30", "20:00"],
                    },
                    8: {
                        3: ["12:30", "20:30"],
                        27: ["16:30"],
                    },
                },
            },
            {2025: [3], 2026: [5, 8]},
        ),
    ],        
)
def test_get_years_with_months(slots, expected_result):
    assert get_years_with_months(slots) == expected_result


@pytest.mark.parametrize(
    "slots,expected_result",
    [
        ({}, {}),
        (
            {
                2025: {3: {18: ["10:00"]}},
                2026: {
                    5: {
                        22: ["18:00", "18:30", "20:00"],
                    },
                    8: {
                        3: ["12:30", "20:30"],
                        27: ["16:30"],
                    },
                },
            },
            {
                2025: {3: [18]},
                2026: {
                    5: [22],
                    8: [3, 27],
                },
            },
        ),
    ],        
)
def test_get_years_with_months_days(slots, expected_result):
    assert get_years_with_months_days(slots) == expected_result


@pytest.mark.parametrize(
    "datetime_,dest_tz,expected_result",
    [
        (
            datetime(2025, 4, 12, 15, 0, tzinfo=UTC),
            pytz.timezone("Europe/Moscow"),
            datetime(2025, 4, 12, 18, 0, tzinfo=timezone(timedelta(hours=3))),
        ),
        (
            datetime(2025, 4, 12, 15, 0, tzinfo=UTC),
            pytz.timezone("Europe/London"),
            datetime(2025, 4, 12, 16, 0, tzinfo=timezone(timedelta(hours=1))),
        ),
        (
            datetime(2025, 4, 12, 15, 0, tzinfo=UTC),
            pytz.timezone("America/New_York"),
            datetime(2025, 4, 12, 8, 0, tzinfo=timezone(timedelta(hours=-7))),
        ),
        (
            datetime(2025, 4, 12, 15, 0),
            pytz.timezone("Europe/Moscow"),
            datetime(2025, 4, 12, 18, 0, tzinfo=timezone(timedelta(hours=3))),
        ),
    ],
)
def test_from_utc(datetime_, dest_tz, expected_result):
    assert from_utc(datetime_, dest_tz) == expected_result


@pytest.mark.parametrize(
    "datetime_,expected_result",
    [
        (
            datetime(2025, 4, 12, 18, 0, tzinfo=timezone(timedelta(hours=3))),
            datetime(2025, 4, 12, 15, 0, tzinfo=UTC),
        ),
        (
            pytz.timezone("Europe/Moscow").localize(datetime(2025, 4, 12, 18, 0)),
            datetime(2025, 4, 12, 15, 0, tzinfo=UTC),
        ),
        (
            datetime(2025, 4, 12, 16, 0, tzinfo=timezone(timedelta(hours=1))),
            datetime(2025, 4, 12, 15, 0, tzinfo=UTC),
        ),
        (
            datetime(2025, 4, 12, 8, 0, tzinfo=timezone(timedelta(hours=-7))),
            datetime(2025, 4, 12, 15, 0, tzinfo=UTC),
        ),
        (
            datetime(2026, 9, 11, 0, 0, tzinfo=timezone(timedelta(hours=3))),
            datetime(2026, 9, 10, 21, 0, tzinfo=UTC),
        ),
    ],
)
def test_to_utc(datetime_, expected_result):
    assert to_utc(datetime_) == expected_result



DURATION_SHOULD_BE_INTEGER = "Длительность должна быть целым числом"
DURATION_SHOULD_BE_GT_0 = "Длительность должна быть больше 0"
DURATION_SHOULD_BE_LTE_MAX_DURATION = "Длительность должна быть менее 1000 минут"
DURATION_SHOULD_BE_A_MULTIPLE_OF_N = "Длительность должна быть кратна 30"
WRONG_FORMAT = "Неверный формат записи числа"


@pytest.mark.parametrize(
    "user_input,expected_result",
    [
        ("30", 30),
        ("120", 120),
        ("    30    ", 30),
        ("\t    120\n", 120),
        ("0", DURATION_SHOULD_BE_GT_0),
        ("+0", DURATION_SHOULD_BE_GT_0),
        ("-0", DURATION_SHOULD_BE_GT_0),
        ("0.0", DURATION_SHOULD_BE_INTEGER),
        ("+0.0", DURATION_SHOULD_BE_INTEGER),
        ("-0.0", DURATION_SHOULD_BE_INTEGER),
        ("990", 990),
        ("999", DURATION_SHOULD_BE_A_MULTIPLE_OF_N),
        ("1000", DURATION_SHOULD_BE_LTE_MAX_DURATION),
        ("1500", DURATION_SHOULD_BE_LTE_MAX_DURATION),
        ("1050.5", DURATION_SHOULD_BE_INTEGER),
        ("1", DURATION_SHOULD_BE_A_MULTIPLE_OF_N),
        ("99", DURATION_SHOULD_BE_A_MULTIPLE_OF_N),
        ("1.001", DURATION_SHOULD_BE_INTEGER),
        ("1.1", DURATION_SHOULD_BE_INTEGER),
        ("1,011", DURATION_SHOULD_BE_INTEGER),
        ("99.999", DURATION_SHOULD_BE_INTEGER),
        ("2.1250000000000000000", DURATION_SHOULD_BE_INTEGER),
        ("    2    ", DURATION_SHOULD_BE_A_MULTIPLE_OF_N),
        ("\t  2.012\n   ", DURATION_SHOULD_BE_INTEGER),
        ("+30", 30),
        ("-30", DURATION_SHOULD_BE_GT_0),
        ("-1", DURATION_SHOULD_BE_GT_0),
        ("+2.1250000000000000000", DURATION_SHOULD_BE_INTEGER),
        ("    +2.012    ", DURATION_SHOULD_BE_INTEGER),
        ("+2,5", DURATION_SHOULD_BE_INTEGER),
        ("+1", DURATION_SHOULD_BE_A_MULTIPLE_OF_N),
        ("+1.0", DURATION_SHOULD_BE_INTEGER),
        ("-2.1250000000000000000", DURATION_SHOULD_BE_INTEGER),
        ("-    2.012    ", DURATION_SHOULD_BE_INTEGER),
        ("    -2.012    ", DURATION_SHOULD_BE_INTEGER),
        ("    2.012-    ", DURATION_SHOULD_BE_INTEGER),
        ("    2.012    -", DURATION_SHOULD_BE_INTEGER),
        ("2-", DURATION_SHOULD_BE_INTEGER),
        ("-2-", DURATION_SHOULD_BE_INTEGER),
        ("2.-", DURATION_SHOULD_BE_INTEGER),
        ("2+", DURATION_SHOULD_BE_INTEGER),
        ("+2+", DURATION_SHOULD_BE_INTEGER),
        ("9+9", DURATION_SHOULD_BE_INTEGER),
        ("1.+05", DURATION_SHOULD_BE_INTEGER),
        ("+2.+1250000000000000000", DURATION_SHOULD_BE_INTEGER),
        ("2.125000000000+0000000", DURATION_SHOULD_BE_INTEGER),
        ("2.1250000000000000000+", DURATION_SHOULD_BE_INTEGER),
        ("+    2.012    ", DURATION_SHOULD_BE_INTEGER),
        ("    2.012+    ", DURATION_SHOULD_BE_INTEGER),
        ("    2.012    +", DURATION_SHOULD_BE_INTEGER),
        ("2+", DURATION_SHOULD_BE_INTEGER),
        ("+2+", DURATION_SHOULD_BE_INTEGER),
        ("2.+", DURATION_SHOULD_BE_INTEGER),
        ("+2-", DURATION_SHOULD_BE_INTEGER),
        ("-2+", DURATION_SHOULD_BE_INTEGER),
        ("-2,5", DURATION_SHOULD_BE_INTEGER),
        ("02.5", WRONG_FORMAT),
        ("002.01250000000000000000", WRONG_FORMAT),
        ("2.5-3.1", DURATION_SHOULD_BE_INTEGER),
        ("2.52.5", DURATION_SHOULD_BE_INTEGER),
        ("2,52,5", DURATION_SHOULD_BE_INTEGER),
        ("2.52,5", DURATION_SHOULD_BE_INTEGER),
        ("2.2 5", DURATION_SHOULD_BE_INTEGER),
        ("2 2.5", DURATION_SHOULD_BE_INTEGER),
        ("2,2 5", DURATION_SHOULD_BE_INTEGER),
        ("2 2,5", DURATION_SHOULD_BE_INTEGER),
        ("2.2,5", DURATION_SHOULD_BE_INTEGER),
        (">2", DURATION_SHOULD_BE_INTEGER),
        ("> 2", DURATION_SHOULD_BE_INTEGER),
        ("<2", DURATION_SHOULD_BE_INTEGER),
        ("<= 2", DURATION_SHOULD_BE_INTEGER),
        ("больше 2.5", DURATION_SHOULD_BE_INTEGER),
        ("aaa", DURATION_SHOULD_BE_INTEGER),
        ("a" * 10, DURATION_SHOULD_BE_INTEGER),
        ("2" * 10, DURATION_SHOULD_BE_LTE_MAX_DURATION),
        ("2" * 10 + "." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("0" + "." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("2..", DURATION_SHOULD_BE_INTEGER),
        ("2e+05", WRONG_FORMAT),
        ("2E+5", WRONG_FORMAT),
        ("2e5", WRONG_FORMAT),
        ("2E-03", WRONG_FORMAT),
        ("2e-3", WRONG_FORMAT),
        ("200.2E-3", WRONG_FORMAT),
        ("200.2e+3", WRONG_FORMAT),
        ("-2.0125", DURATION_SHOULD_BE_INTEGER),
        ("2.0125-", DURATION_SHOULD_BE_INTEGER),
        ("2,0125+", DURATION_SHOULD_BE_INTEGER),
        ("-02.5", WRONG_FORMAT),
        ("02.5-", WRONG_FORMAT),
        ("+02.5", WRONG_FORMAT),
        ("02.5+", WRONG_FORMAT),
        ("-002.01250000000000000000", WRONG_FORMAT),
        ("+002.01250000000000000000", WRONG_FORMAT),
        ("002.01250000000000000000-", WRONG_FORMAT),
        ("002.01250000000000000000+", WRONG_FORMAT),
        ("-2.5-3.1", DURATION_SHOULD_BE_INTEGER),
        ("+2.5-3.1", DURATION_SHOULD_BE_INTEGER),
        ("2.5+3.1", DURATION_SHOULD_BE_INTEGER),
        ("-2.52.5", DURATION_SHOULD_BE_INTEGER),
        ("2,52,5-", DURATION_SHOULD_BE_INTEGER),
        ("+2.52,5", DURATION_SHOULD_BE_INTEGER),
        ("2.52,5+", DURATION_SHOULD_BE_INTEGER),
        ("-2.2 5", DURATION_SHOULD_BE_INTEGER),
        ("2 2.5-", DURATION_SHOULD_BE_INTEGER),
        ("+2,2 5", DURATION_SHOULD_BE_INTEGER),
        ("2 2,5+", DURATION_SHOULD_BE_INTEGER),
        ("-" + "2" * 10, DURATION_SHOULD_BE_GT_0),
        ("2" * 10 + "-", DURATION_SHOULD_BE_INTEGER),
        ("+" + "2" * 10, DURATION_SHOULD_BE_LTE_MAX_DURATION),
        ("2" * 10 + "+", DURATION_SHOULD_BE_INTEGER),
        ("-" + "2" * 10 + "." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("2" * 10 + "." + "2" * 10 + "-", DURATION_SHOULD_BE_INTEGER),
        ("+" + "2" * 10 + "." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("2" * 10 + "." + "2" * 10 + "+", DURATION_SHOULD_BE_INTEGER),
        ("-0" + "." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("0" + "." + "2" * 10 + "-", DURATION_SHOULD_BE_INTEGER),
        ("+0" + "." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("0" + "." + "2" * 10 + "+", DURATION_SHOULD_BE_INTEGER),
        ("-2..", DURATION_SHOULD_BE_INTEGER),
        ("2..-", DURATION_SHOULD_BE_INTEGER),
        ("2.-.", DURATION_SHOULD_BE_INTEGER),
        ("+2..", DURATION_SHOULD_BE_INTEGER),
        ("2..+", DURATION_SHOULD_BE_INTEGER),
        ("2.+.", DURATION_SHOULD_BE_INTEGER),
        (".5-", DURATION_SHOULD_BE_INTEGER),
        (".5+", DURATION_SHOULD_BE_INTEGER),
        ("-2e+05", WRONG_FORMAT),
        ("2E+5-", WRONG_FORMAT),
        ("+2e5", WRONG_FORMAT),
        ("2e5+", WRONG_FORMAT),
        ("-2E-03", WRONG_FORMAT),
        ("2e-3-", WRONG_FORMAT),
        ("+200.2E-3", WRONG_FORMAT),
        ("200.2e+3+", WRONG_FORMAT),
        ("-0." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("0." + "2" * 10 + "-", DURATION_SHOULD_BE_INTEGER),
        ("+0." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("0." + "2" * 10 + "+", DURATION_SHOULD_BE_INTEGER),
        ("-" + "2" * 10, DURATION_SHOULD_BE_GT_0),
        ("2" * 10 + "-", DURATION_SHOULD_BE_INTEGER),
        ("+" + "2" * 10, DURATION_SHOULD_BE_LTE_MAX_DURATION),
        ("2" * 10 + "+", DURATION_SHOULD_BE_INTEGER),
        ("-" + "2" * 10 + "." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("2" * 10 + ".-" + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("2" * 10 + "." + "2" * 10 + "-", DURATION_SHOULD_BE_INTEGER),
        ("+" + "2" * 10 + "." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("2" * 10 + ".+" + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("2" * 10 + "." + "2" * 10 + "+", DURATION_SHOULD_BE_INTEGER),
        ("2" * 10, DURATION_SHOULD_BE_LTE_MAX_DURATION),
        ("2" * 10 + "." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("-200.2e+" + "3" * 10, WRONG_FORMAT),
        ("200.2e+" + "3" * 10 + "-", WRONG_FORMAT),
        ("+200.2e+" + "3" * 10, WRONG_FORMAT),
        ("200.2e+" + "3" * 10 + "+", WRONG_FORMAT),
        ("-0." + "2" * 10 + "e+05", WRONG_FORMAT),
        ("0." + "2" * 10 + "e+05-", WRONG_FORMAT),
        ("+0." + "2" * 10 + "e+05", WRONG_FORMAT),
        ("0." + "2" * 10 + "e+05+", WRONG_FORMAT),
        ("-" + "2" * 10 + "E+5", WRONG_FORMAT),
        ("2" * 10 + "E+5-", WRONG_FORMAT),
        ("+" + "2" * 10 + "E+5", WRONG_FORMAT),
        ("2" * 10 + "E+5+", WRONG_FORMAT),
        ("-2." + "2" * 10 + "E-03", WRONG_FORMAT),
        ("2." + "2" * 10 + "E-03-", WRONG_FORMAT),
        ("+2." + "2" * 10 + "E-03", WRONG_FORMAT),
        ("2." + "2" * 10 + "E-03+", WRONG_FORMAT),
        ("-" + "2" * 10 + "." + "2" * 10 + "e-3", WRONG_FORMAT),
        ("2" * 10 + ".-" + "2" * 10 + "e-3", WRONG_FORMAT),
        ("2" * 10 + "." + "2" * 10 + "e-3-", WRONG_FORMAT),
        ("+" + "2" * 10 + "." + "2" * 10 + "e-3", WRONG_FORMAT),
        ("2" * 10 + "+." + "2" * 10 + "e-3", WRONG_FORMAT),
        ("2" * 10 + "." + "2" * 10 + "e-3+", WRONG_FORMAT),
        ("200.2e+" + "3" * 10, WRONG_FORMAT),
        ("0." + "2" * 10 + "e+05", WRONG_FORMAT),
        ("2" * 10 + "E+5", WRONG_FORMAT),
        ("2." + "2" * 10 + "E-03", WRONG_FORMAT),
        ("2" * 10 + "." + "2" * 10 + "e-3", WRONG_FORMAT),
        ("2.", WRONG_FORMAT),
        ("0." + "2" * 10, DURATION_SHOULD_BE_INTEGER),
        ("+2.", WRONG_FORMAT),
        ("2,", WRONG_FORMAT),
        ("+2,", WRONG_FORMAT),
        ("-2.", WRONG_FORMAT),
        (".5", WRONG_FORMAT),
        ("-.5", WRONG_FORMAT),
        ("+.5", WRONG_FORMAT),
    ],
)
def test_validate_service_duration(user_input, expected_result):
    assert validate_service_duration(user_input) == expected_result
