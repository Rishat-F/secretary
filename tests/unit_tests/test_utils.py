from datetime import datetime

import pytest

from src.utils import (
    get_datetimes_needed_for_appointment,
    get_times_for_appointment,
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
def test_get_slot_numbers_needed_for_appointment(starts_at, duration, expected_datetimes):
    assert get_datetimes_needed_for_appointment(starts_at, duration) == expected_datetimes
