from datetime import datetime

import pytest

from src.business_logic.resolve_days_statuses.utils import (
    get_days_statuses,
    get_selected_days_view,
)


@pytest.mark.parametrize(
    "tz_now,selected_dates,chosen_year,chosen_month,expected_result",
    [
        (
            datetime(2025, 2, 5),
            [],
            2025,
            2,
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            datetime(2024, 9, 22),
            [],
            2024,
            9,
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2024-09-01",
                "not_available_week2", "not_available_2024-09-02", "not_available_2024-09-03", "not_available_2024-09-04", "not_available_2024-09-05", "not_available_2024-09-06", "not_available_2024-09-07", "not_available_2024-09-08",
                "not_available_week3", "not_available_2024-09-09", "not_available_2024-09-10", "not_available_2024-09-11", "not_available_2024-09-12", "not_available_2024-09-13", "not_available_2024-09-14", "not_available_2024-09-15",
                "not_selected_week4", "not_available_2024-09-16", "not_available_2024-09-17", "not_available_2024-09-18", "not_available_2024-09-19", "not_available_2024-09-20", "not_available_2024-09-21", "not_selected_2024-09-22",
                "not_selected_week5", "not_selected_2024-09-23", "not_selected_2024-09-24", "not_selected_2024-09-25", "not_selected_2024-09-26", "not_selected_2024-09-27", "not_selected_2024-09-28", "not_selected_2024-09-29",
                "not_selected_week6", "not_selected_2024-09-30", "ignore", "ignore", "ignore", "ignore", "ignore", "ignore",
            ],
        ),

        (
            datetime(2025, 2, 5),
            ["2025-01-31", "2025-02-03", "2025-02-12", "2025-02-27"],
            2025,
            2,
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "selected_wednesday", "selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            datetime(2025, 1, 5),
            ["2025-03-25"],
            2025,
            2,
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_selected_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_selected_2025-02-01", "not_selected_2025-02-02",
                "not_selected_week2", "not_selected_2025-02-03", "not_selected_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            datetime(2025, 2, 27),
            ["2025-02-25", "2025-02-28"],
            2025,
            2,
            [
                "selected_all", "not_available_monday", "not_available_tuesday", "not_available_wednesday", "not_selected_thursday", "selected_friday", "not_available_saturday", "not_available_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_available_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_available_2025-02-05", "not_available_2025-02-06", "not_available_2025-02-07", "not_available_2025-02-08", "not_available_2025-02-09",
                "not_available_week3", "not_available_2025-02-10", "not_available_2025-02-11", "not_available_2025-02-12", "not_available_2025-02-13", "not_available_2025-02-14", "not_available_2025-02-15", "not_available_2025-02-16",
                "not_available_week4", "not_available_2025-02-17", "not_available_2025-02-18", "not_available_2025-02-19", "not_available_2025-02-20", "not_available_2025-02-21", "not_available_2025-02-22", "not_available_2025-02-23",
                "selected_week5", "not_available_2025-02-24", "not_available_2025-02-25", "not_available_2025-02-26", "not_selected_2025-02-27", "selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            datetime(2025, 2, 27),
            [],
            None,
            None,
            [
                "not_selected_all", "not_available_monday", "not_available_tuesday", "not_available_wednesday", "not_selected_thursday", "not_selected_friday", "not_available_saturday", "not_available_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_available_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_available_2025-02-05", "not_available_2025-02-06", "not_available_2025-02-07", "not_available_2025-02-08", "not_available_2025-02-09",
                "not_available_week3", "not_available_2025-02-10", "not_available_2025-02-11", "not_available_2025-02-12", "not_available_2025-02-13", "not_available_2025-02-14", "not_available_2025-02-15", "not_available_2025-02-16",
                "not_available_week4", "not_available_2025-02-17", "not_available_2025-02-18", "not_available_2025-02-19", "not_available_2025-02-20", "not_available_2025-02-21", "not_available_2025-02-22", "not_available_2025-02-23",
                "not_selected_week5", "not_available_2025-02-24", "not_available_2025-02-25", "not_available_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

    ]
)
def test_get_days_statuses(tz_now, selected_dates, chosen_year, chosen_month, expected_result):
    result = get_days_statuses(tz_now, selected_dates, chosen_year, chosen_month)
    assert result == expected_result


@pytest.mark.parametrize(
    "days,expected_result",
    [
        ([], ""),
        ([1], "1"),
        ([25], "25"),
        ([2, 8], "2, 8"),
        ([1, 2], "1-2"),
        ([1, 2, 3, 4, 5], "1-5"),
        ([1, 4, 5, 6], "1, 4-6"),
        ([1, 5, 6], "1, 5-6"),
        ([1, 3, 5, 6, 9, 10, 11, 12, 22, 23, 24], "1, 3, 5-6, 9-12, 22-24"),
    ]
)
def test_get_selected_days_view(days, expected_result):
    assert get_selected_days_view(days) == expected_result
