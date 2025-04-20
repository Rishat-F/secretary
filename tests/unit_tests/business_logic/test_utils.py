from datetime import datetime

import pytest

from src.business_logic.utils import (
    MINIMAL_TIMES_STATUSES_LEN,
    TIMES_STATUSES_LEN,
    _get_duration_multiplier_by_times_statues,
    _get_times_statuses_len,
    _no_isolated_selected,
    _no_selected_edge_combination,
    _no_edge_selected_combination,
    check_clicked_index_assertions,
    check_chosen_datetime_is_possible,
    check_times_statuses_assertions,
    get_datetimes_needed_for_appointment,
    get_months_keyboard_buttons,
    get_times_for_appointment,
    get_times_statuses_view,
    get_years_keyboard_buttons,
    get_years_with_months,
    get_years_with_months_days,
    initial_times_statuses,
)
from src.exceptions import (
    DayBecomeNotAvailable,
    MonthBecomeNotAvailable,
    TimeBecomeNotAvailable,
    YearBecomeNotAvailable,
)
from src.keyboards import InlineButton


def test_times_statuses_len():
    assert TIMES_STATUSES_LEN == 49


def test_minimal_times_statuses_len():
    assert MINIMAL_TIMES_STATUSES_LEN == 3


def test_initial_times_statuses():
    assert initial_times_statuses == ["not_selected"] * 49


@pytest.mark.parametrize(
    "duration_multiplier,expected_result",
    [
        (720, 3),
        (480, 4),
        (360, 5),
        (240, 7),
        (120, 13),
        (60, 25),
        (30, 49),
        (20, 73),
        (15, 97),
        (10, 145),
        (5, 289),
    ],
)
def test__get_times_statuses_len(duration_multiplier, expected_result):
    assert _get_times_statuses_len(duration_multiplier) == expected_result


@pytest.mark.parametrize(
    "times_statuses_len,expected_result",
    [
        (3, 720),
        (4, 480),
        (5, 360),
        (7, 240),
        (13, 120),
        (25, 60),
        (49, 30),
        (73, 20),
        (97, 15),
        (145, 10),
        (289, 5),
    ],
)
def test__get_duration_multiplier_by_times_statues(times_statuses_len, expected_result):
    assert _get_duration_multiplier_by_times_statues(times_statuses_len) == expected_result


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (["not_selected", "not_selected", "not_selected"], True),
        (["not_selected", "not_selected", "selected"], False),
        (["not_selected", "not_selected", "edge"], True),
        (["not_selected", "selected", "not_selected"], False),
        (["not_selected", "selected", "selected"], True),
        (["not_selected", "selected", "edge"], False),
        (["not_selected", "edge", "not_selected"], True),
        (["not_selected", "edge", "selected"], False),
        (["not_selected", "edge", "edge"], True),
        (["selected", "not_selected", "not_selected"], False),
        (["selected", "not_selected", "selected"], False),
        (["selected", "not_selected", "edge"], False),
        (["selected", "selected", "not_selected"], True),
        (["selected", "selected", "selected"], True),
        (["selected", "selected", "edge"], True),
        (["selected", "edge", "not_selected"], False),
        (["selected", "edge", "selected"], False),
        (["selected", "edge", "edge"], False),
        (["edge", "not_selected", "not_selected"], True),
        (["edge", "not_selected", "selected"], False),
        (["edge", "not_selected", "edge"], True),
        (["edge", "selected", "not_selected"], False),
        (["edge", "selected", "selected"], True),
        (["edge", "selected", "edge"], False),
        (["edge", "edge", "not_selected"], True),
        (["edge", "edge", "selected"], False),
        (["edge", "edge", "edge"], True),
        (
            [
                "not_selected",
                "not_selected",
                "not_selected",
                "not_selected",
                "not_selected",
                "not_selected",
                "not_selected",
            ],
            True,
        ),
        (
            [
                "selected",
                "selected",
                "selected",
                "selected",
                "selected",
                "selected",
                "selected",
            ],
            True,
        ),
        (
            [
                "edge",
                "not_selected",
                "selected",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
            ],
            False,
        ),
        (
            [
                "not_seledted",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
            ],
            False,
        ),
        (
            [
                "selected",
                "not_seledted",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
                "selected",
                "not_selected",
                "selected",
            ],
            False,
        ),
    ],
)
def test__no_isolated_selected(times_statuses, expected_result):
    assert _no_isolated_selected(times_statuses) is expected_result


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (["not_selected", "not_selected", "not_selected"], True),
        (["not_selected", "not_selected", "selected"], True),
        (["not_selected", "not_selected", "edge"], True),
        (["not_selected", "selected", "not_selected"], True),
        (["not_selected", "selected", "selected"], True),
        (["not_selected", "selected", "edge"], True),
        (["not_selected", "edge", "not_selected"], True),
        (["not_selected", "edge", "selected"], False),
        (["not_selected", "edge", "edge"], True),
        (["selected", "not_selected", "not_selected"], True),
        (["selected", "not_selected", "selected"], True),
        (["selected", "not_selected", "edge"], True),
        (["selected", "selected", "not_selected"], True),
        (["selected", "selected", "selected"], True),
        (["selected", "selected", "edge"], True),
        (["selected", "edge", "not_selected"], True),
        (["selected", "edge", "selected"], False),
        (["selected", "edge", "edge"], True),
        (["edge", "not_selected", "not_selected"], True),
        (["edge", "not_selected", "selected"], True),
        (["edge", "not_selected", "edge"], True),
        (["edge", "selected", "not_selected"], False),
        (["edge", "selected", "selected"], False),
        (["edge", "selected", "edge"], False),
        (["edge", "edge", "not_selected"], True),
        (["edge", "edge", "selected"], False),
        (["edge", "edge", "edge"], True),
    ],
)
def test__no_edge_selected_combination(times_statuses, expected_result):
    assert _no_edge_selected_combination(times_statuses) is expected_result


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (["not_selected", "not_selected", "not_selected"], True),
        (["not_selected", "not_selected", "selected"], True),
        (["not_selected", "not_selected", "edge"], True),
        (["not_selected", "selected", "not_selected"], True),
        (["not_selected", "selected", "selected"], True),
        (["not_selected", "selected", "edge"], False),
        (["not_selected", "edge", "not_selected"], True),
        (["not_selected", "edge", "selected"], True),
        (["not_selected", "edge", "edge"], True),
        (["selected", "not_selected", "not_selected"], True),
        (["selected", "not_selected", "selected"], True),
        (["selected", "not_selected", "edge"], True),
        (["selected", "selected", "not_selected"], True),
        (["selected", "selected", "selected"], True),
        (["selected", "selected", "edge"], False),
        (["selected", "edge", "not_selected"], False),
        (["selected", "edge", "selected"], False),
        (["selected", "edge", "edge"], False),
        (["edge", "not_selected", "not_selected"], True),
        (["edge", "not_selected", "selected"], True),
        (["edge", "not_selected", "edge"], True),
        (["edge", "selected", "not_selected"], True),
        (["edge", "selected", "selected"], True),
        (["edge", "selected", "edge"], False),
        (["edge", "edge", "not_selected"], True),
        (["edge", "edge", "selected"], True),
        (["edge", "edge", "edge"], True),
    ],
)
def test__no_selected_edge_combination(times_statuses, expected_result):
    assert _no_selected_edge_combination(times_statuses) is expected_result


@pytest.mark.parametrize(
    "times_statuses",
    [
        ["not_selected", "not_selected", "not_selected"],
        ["not_selected", "not_selected", "edge"],
        ["not_selected", "selected", "selected"],
        ["not_selected", "edge", "not_selected"],
        ["selected", "selected", "not_selected"],
        ["selected", "selected", "selected"],
        ["edge", "not_selected", "not_selected"],
        [
            "not_selected",
            "edge",
            "not_selected",
            "selected",
            "selected",
            "not_selected",
            "selected",
            "selected",
            "not_selected",
        ],
    ],
)
def test_check_times_statuses_assertions_passes(
    times_statuses,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.utils.TIMES_STATUSES_LEN", len(times_statuses))
    assert check_times_statuses_assertions(times_statuses) is None


@pytest.mark.parametrize(
    "times_statuses",
    [
        ["not_selected", "not_selected", "selected"],
        ["not_selected", "selected", "not_selected"],
        ["not_selected", "selected", "edge"],
        ["not_selected", "edge", "selected"],
        ["not_selected", "edge", "edge"],
        ["selected", "not_selected", "not_selected"],
        ["selected", "not_selected", "selected"],
        ["selected", "not_selected", "edge"],
        ["selected", "selected", "edge"],
        ["selected", "edge", "not_selected"],
        ["selected", "edge", "selected"],
        ["selected", "edge", "edge"],
        ["edge", "not_selected", "selected"],
        ["edge", "not_selected", "edge"],
        ["edge", "selected", "not_selected"],
        ["edge", "selected", "selected"],
        ["edge", "selected", "edge"],
        ["edge", "edge", "not_selected"],
        ["edge", "edge", "selected"],
        ["edge", "edge", "edge"],
        ["not_selected", "not_selected", "not_selected", "not_selected"],
        ["not_selected", "finish", "not_selected"],
    ],
)
def test_check_times_statuses_assertions_raises_assertion_error(
    times_statuses,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.utils.TIMES_STATUSES_LEN", 3)
    with pytest.raises(AssertionError):
        check_times_statuses_assertions(times_statuses)


@pytest.mark.parametrize("clicked_index", [0, 1, 2])
def test_check_clicked_index_assertions_passes(
    clicked_index,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.utils.TIMES_STATUSES_LEN", 3)
    assert check_clicked_index_assertions(clicked_index) is None


@pytest.mark.parametrize("clicked_index", [-10, -1, 3, 5, 10])
def test_check_clicked_index_assertions_raises_assertion_error(
    clicked_index,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.business_logic.utils.TIMES_STATUSES_LEN", 3)
    with pytest.raises(AssertionError):
        check_clicked_index_assertions(clicked_index)


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (
            ["not_selected", "not_selected", "not_selected", "not_selected"],
            "Рабочие часы не выбраны",
        ),
        (
            ["edge", "not_selected", "not_selected", "not_selected"],
            "Выбранные рабочие часы:\n00:00-...",
        ),
        (
            ["not_selected", "not_selected", "not_selected", "edge"],
            "Выбранные рабочие часы:\n...-00:00",
        ),
        (
            ["not_selected", "edge", "not_selected", "not_selected"],
            "Выбранные рабочие часы:\n...-08:00-...",
        ),
        (
            ["selected", "selected", "selected"],
            "Выбранные рабочие часы:\n00:00-00:00",
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            "Выбранные рабочие часы:\n00:00-00:00",
        ),
        (
            ["edge", "not_selected", "selected", "selected", "not_selected"],
            "Выбранные рабочие часы:\n00:00-...\n12:00-18:00",
        ),
        (
            ["selected", "selected", "not_selected", "edge", "not_selected"],
            "Выбранные рабочие часы:\n00:00-06:00\n...-18:00-...",
        ),
        (
            ["selected", "selected", "not_selected", "selected", "selected"],
            "Выбранные рабочие часы:\n00:00-06:00\n18:00-00:00",
        ),
        (
            [
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected",
            ],
            "Выбранные рабочие часы:\n00:00-00:00",
        ),
        (
            [
                "selected", "selected", "not_selected", "not_selected",
                "selected", "selected", "selected", "not_selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected",
            ],
            "Выбранные рабочие часы:\n00:00-00:30\n02:00-03:00\n04:00-06:30\n16:00-00:00",
        ),
        (
            [
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "not_selected", "selected", "selected",
                "selected", "selected", "selected", "selected",
                "selected", "selected", "selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected", "not_selected", "not_selected", "not_selected",
                "not_selected",
            ],
            "Выбранные рабочие часы:\n08:00-12:00\n13:00-17:00",
        ),
    ],
)
def test_get_times_statuses_view(times_statuses, expected_result):
    assert get_times_statuses_view(times_statuses) == expected_result


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
def test_get_months_keyboard_buttons(years_with_months, current_year, current_month, chosen_year, expected_result):
    now_ = datetime(current_year, current_month, 15)
    assert get_months_keyboard_buttons(years_with_months, now_, chosen_year) == expected_result


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
    assert get_years_keyboard_buttons(years, now_) == expected_result


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
