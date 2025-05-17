import pytest

from src.business_logic.schedule.utils import (
    get_all_times_len,
    _get_all_times,
    _get_schedule_times_from_to,
    _get_times_buttons_for_view_schedule,
)
from src.keyboards import InlineButton


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
def test_get_all_times_len(duration_multiplier, expected_result):
    assert get_all_times_len(duration_multiplier) == expected_result


@pytest.mark.parametrize(
    "duration_multiplier,expected_result",
    [
        (360, [ "00:00", "06:00", "12:00", "18:00", "00:00"]),
        (
            30,
            [
                "00:00", "00:30", "01:00", "01:30", "02:00", "02:30", "03:00", "03:30",
                "04:00", "04:30", "05:00", "05:30", "06:00", "06:30", "07:00", "07:30",
                "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
                "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
                "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
                "20:00", "20:30", "21:00", "21:30", "22:00", "22:30", "23:00", "23:30",
                "00:00"
            ],
        ),
    ],
)
def test__get_all_times(duration_multiplier, expected_result):
    result = _get_all_times(duration_multiplier)
    assert result == expected_result


@pytest.mark.parametrize(
    "schedule_times,duration_multiplier,expected_result",
    [
        (
            ["00:00"],
            360,
            ["00:00", "06:00"],
        ),
        (
            ["06:00", "12:00"],
            360,
            ["06:00", "12:00", "18:00"],
        ),
        (
            ["18:00"],
            360,
            ["18:00", "00:00"],
        ),
        (
            ["00:00", "06:00", "12:00", "18:00"],
            360,
            ["00:00", "06:00", "12:00", "18:00", "00:00"],
        ),
        (
            ["06:00", "18:00", "00:00", "12:00"],
            360,
            ["00:00", "06:00", "12:00", "18:00", "00:00"],
        ),
    ],
)
def test__get_schedule_times_from_to(schedule_times, duration_multiplier, expected_result):
    result = _get_schedule_times_from_to(schedule_times, duration_multiplier)
    assert result == expected_result


@pytest.mark.parametrize(
    "all_times,schedule_times_from_to,expected_result",
    [
        (
            ["00:00", "06:00", "12:00", "18:00", "00:00"],
            ["00:00", "06:00", "12:00", "18:00", "00:00"],
            [
                InlineButton("ignore", "00:00", "00:00"),
                InlineButton("ignore", "06:00", "06:00"),
                InlineButton("ignore", "12:00", "12:00"),
                InlineButton("ignore", "18:00", "18:00"),
                InlineButton("ignore", "00:00", "00:00"),
            ],
        ),
        (
            ["00:00", "06:00", "12:00", "18:00", "00:00"],
            ["06:00", "12:00"],
            [
                InlineButton("ignore", " ", "00:00"),
                InlineButton("ignore", "06:00", "06:00"),
                InlineButton("ignore", "12:00", "12:00"),
                InlineButton("ignore", " ", "18:00"),
                InlineButton("ignore", " ", "00:00"),
            ],
        ),
        (
            ["00:00", "06:00", "12:00", "18:00", "00:00"],
            ["00:00", "06:00", "12:00", "18:00"],
            [
                InlineButton("ignore", "00:00", "00:00"),
                InlineButton("ignore", "06:00", "06:00"),
                InlineButton("ignore", "12:00", "12:00"),
                InlineButton("ignore", "18:00", "18:00"),
                InlineButton("ignore", " ", "00:00"),
            ],
        ),
        (
            ["00:00", "06:00", "12:00", "18:00", "00:00"],
            ["06:00", "12:00", "18:00", "00:00"],
            [
                InlineButton("ignore", " ", "00:00"),
                InlineButton("ignore", "06:00", "06:00"),
                InlineButton("ignore", "12:00", "12:00"),
                InlineButton("ignore", "18:00", "18:00"),
                InlineButton("ignore", "00:00", "00:00"),
            ],
        ),
    ],
)
def test__get_times_buttons_for_view_schedule(all_times, schedule_times_from_to, expected_result):
    result = _get_times_buttons_for_view_schedule(all_times, schedule_times_from_to)
    assert result == expected_result
