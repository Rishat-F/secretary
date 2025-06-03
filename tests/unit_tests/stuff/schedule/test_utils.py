from datetime import datetime

import pytest

from src.stuff.schedule.keyboards import InlineButton
from src.stuff.schedule.utils import (
    MINIMAL_TIMES_STATUSES_LEN,
    TIMES_STATUSES_LEN,
    _get_all_times,
    _get_month_selected_days_view,
    _get_schedule_times_from_to,
    _get_times_buttons_for_view_schedule,
    _get_duration_multiplier_by_times_statuses,
    _no_edge_selected_combination,
    _no_isolated_selected,
    _no_selected_edge_combination,
    actualize_groups_selection_status,
    check_clicked_index_assertions,
    check_times_statuses_assertions,
    get_all_times_len,
    get_days_statuses,
    get_initial_times_statuses,
    get_selected_times,
    get_slots_to_delete,
    get_slots_to_save,
    get_times_statuses_view,
    get_working_hours_view,
    resolve_days_statuses,
    resolve_times_statuses,
)


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
def test__get_month_selected_days_view(days, expected_result):
    assert _get_month_selected_days_view(days) == expected_result


@pytest.mark.parametrize(
    "days_statuses,expected_result",
    [
        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_selected_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_available_2025-02-05", "not_available_2025-02-06", "not_available_2025-02-07", "not_available_2025-02-08", "not_available_2025-02-09",
                "not_selected_week3", "not_available_2025-02-10", "not_available_2025-02-11", "not_available_2025-02-12", "not_available_2025-02-13", "not_available_2025-02-14", "not_available_2025-02-15", "not_available_2025-02-16",
                "not_selected_week4", "not_available_2025-02-17", "not_available_2025-02-18", "not_available_2025-02-19", "not_available_2025-02-20", "not_available_2025-02-21", "not_available_2025-02-22", "not_available_2025-02-23",
                "not_selected_week5", "not_available_2025-02-24", "not_available_2025-02-25", "not_available_2025-02-26", "selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            [
                "selected_all", "not_available_monday", "not_available_tuesday", "not_available_wednesday", "selected_thursday", "not_selected_friday", "not_available_saturday", "not_available_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_available_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_available_2025-02-05", "not_available_2025-02-06", "not_available_2025-02-07", "not_available_2025-02-08", "not_available_2025-02-09",
                "not_available_week3", "not_available_2025-02-10", "not_available_2025-02-11", "not_available_2025-02-12", "not_available_2025-02-13", "not_available_2025-02-14", "not_available_2025-02-15", "not_available_2025-02-16",
                "not_available_week4", "not_available_2025-02-17", "not_available_2025-02-18", "not_available_2025-02-19", "not_available_2025-02-20", "not_available_2025-02-21", "not_available_2025-02-22", "not_available_2025-02-23",
                "selected_week5", "not_available_2025-02-24", "not_available_2025-02-25", "not_available_2025-02-26", "selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),
    ],
)
def test_actualize_groups_selection_status(days_statuses, expected_result):
    result = actualize_groups_selection_status(days_statuses)
    assert result == expected_result


@pytest.mark.parametrize(
    "days_statuses,clicked_element,expected_result",
    [
    # all group clicked
        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "not_selected_all",
            [
                "selected_all", "selected_monday", "selected_tuesday", "selected_wednesday", "selected_thursday", "selected_friday", "selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "selected_2025-02-05", "selected_2025-02-06", "selected_2025-02-07", "selected_2025-02-08", "selected_2025-02-09",
                "selected_week3", "selected_2025-02-10", "selected_2025-02-11", "selected_2025-02-12", "selected_2025-02-13", "selected_2025-02-14", "selected_2025-02-15", "selected_2025-02-16",
                "selected_week4", "selected_2025-02-17", "selected_2025-02-18", "selected_2025-02-19", "selected_2025-02-20", "selected_2025-02-21", "selected_2025-02-22", "selected_2025-02-23",
                "selected_week5", "selected_2025-02-24", "selected_2025-02-25", "selected_2025-02-26", "selected_2025-02-27", "selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "selected_monday", "selected_tuesday", "selected_wednesday", "selected_thursday", "selected_friday", "selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "selected_2025-02-05", "selected_2025-02-06", "selected_2025-02-07", "selected_2025-02-08", "selected_2025-02-09",
                "selected_week3", "selected_2025-02-10", "selected_2025-02-11", "selected_2025-02-12", "selected_2025-02-13", "selected_2025-02-14", "selected_2025-02-15", "selected_2025-02-16",
                "selected_week4", "selected_2025-02-17", "selected_2025-02-18", "selected_2025-02-19", "selected_2025-02-20", "selected_2025-02-21", "selected_2025-02-22", "selected_2025-02-23",
                "selected_week5", "selected_2025-02-24", "selected_2025-02-25", "selected_2025-02-26", "selected_2025-02-27", "selected_2025-02-28", "ignore", "ignore",
            ],
            "selected_all",
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
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "selected_2025-02-07", "not_selected_2025-02-08", "selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "selected_all",
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

    # day clicked
        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "not_selected_2025-02-07",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "selected_2025-02-07",
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
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "selected_2025-02-07",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "selected_2025-02-07", "not_selected_2025-02-08", "selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "selected_2025-02-07",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "selected_2025-02-07", "not_selected_2025-02-08", "selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "selected_2025-02-07",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

    # day of week group clicked
        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "not_selected_thursday",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "not_selected_monday",
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "selected_week3", "selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "selected_week5", "selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "selected_week3", "selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "selected_week5", "selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "not_selected_friday",
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "selected_2025-02-06", "selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "selected_week3", "selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "selected_2025-02-13", "selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "selected_2025-02-20", "selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "selected_week5", "selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "selected_2025-02-27", "selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "selected_2025-02-06", "selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "selected_week3", "selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "selected_2025-02-13", "selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "selected_2025-02-20", "selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "selected_week5", "selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "selected_2025-02-27", "selected_2025-02-28", "ignore", "ignore",
            ],
            "selected_thursday",
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "selected_week3", "selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "selected_week4", "selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "selected_week5", "selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "selected_2025-02-28", "ignore", "ignore",
            ],
        ),

    # week group clicked
        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "not_selected_week3",
            [
                "selected_all", "selected_monday", "selected_tuesday", "selected_wednesday", "selected_thursday", "selected_friday", "selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "selected_week3", "selected_2025-02-10", "selected_2025-02-11", "selected_2025-02-12", "selected_2025-02-13", "selected_2025-02-14", "selected_2025-02-15", "selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
        ),

        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "not_selected_week5", "not_selected_2025-02-24", "not_selected_2025-02-25", "not_selected_2025-02-26", "not_selected_2025-02-27", "not_selected_2025-02-28", "ignore", "ignore",
            ],
            "not_selected_week5",
            [
                "selected_all", "selected_monday", "selected_tuesday", "selected_wednesday", "selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_2025-02-01", "not_available_2025-02-02",
                "not_selected_week2", "not_available_2025-02-03", "not_available_2025-02-04", "not_selected_2025-02-05", "not_selected_2025-02-06", "not_selected_2025-02-07", "not_selected_2025-02-08", "not_selected_2025-02-09",
                "not_selected_week3", "not_selected_2025-02-10", "not_selected_2025-02-11", "not_selected_2025-02-12", "not_selected_2025-02-13", "not_selected_2025-02-14", "not_selected_2025-02-15", "not_selected_2025-02-16",
                "not_selected_week4", "not_selected_2025-02-17", "not_selected_2025-02-18", "not_selected_2025-02-19", "not_selected_2025-02-20", "not_selected_2025-02-21", "not_selected_2025-02-22", "not_selected_2025-02-23",
                "selected_week5", "selected_2025-02-24", "selected_2025-02-25", "selected_2025-02-26", "selected_2025-02-27", "selected_2025-02-28", "ignore", "ignore",
            ],
        ),
    ],
)
def test_resolve_days_statuses(days_statuses, clicked_element, expected_result):
    result = resolve_days_statuses(days_statuses, clicked_element)
    assert result == expected_result


def test_times_statuses_len():
    assert TIMES_STATUSES_LEN == 49


def test_minimal_times_statuses_len():
    assert MINIMAL_TIMES_STATUSES_LEN == 3


def test_get_initial_times_statuses():
    assert get_initial_times_statuses() == ["not_selected"] * 49


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
def test__get_duration_multiplier_by_times_statuses(times_statuses_len, expected_result):
    assert _get_duration_multiplier_by_times_statuses(times_statuses_len) == expected_result


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
    monkeypatch.setattr("src.stuff.schedule.utils.TIMES_STATUSES_LEN", len(times_statuses))
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
    monkeypatch.setattr("src.stuff.schedule.utils.TIMES_STATUSES_LEN", 3)
    with pytest.raises(AssertionError):
        check_times_statuses_assertions(times_statuses)


@pytest.mark.parametrize("clicked_index", [0, 1, 2])
def test_check_clicked_index_assertions_passes(
    clicked_index,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.stuff.schedule.utils.TIMES_STATUSES_LEN", 3)
    assert check_clicked_index_assertions(clicked_index) is None


@pytest.mark.parametrize("clicked_index", [-10, -1, 3, 5, 10])
def test_check_clicked_index_assertions_raises_assertion_error(
    clicked_index,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.stuff.schedule.utils.TIMES_STATUSES_LEN", 3)
    with pytest.raises(AssertionError):
        check_clicked_index_assertions(clicked_index)


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (
            ["not_selected", "not_selected", "not_selected", "not_selected"],
            [],
        ),
        (
            ["edge", "not_selected", "not_selected", "not_selected"],
            [],
        ),
        (
            ["not_selected", "not_selected", "not_selected", "edge"],
            [],
        ),
        (
            ["not_selected", "edge", "not_selected", "not_selected"],
            [],
        ),
        (
            ["selected", "selected", "selected"],
            ["00:00", "12:00"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            ["00:00", "06:00", "12:00", "18:00"],
        ),
        (
            ["edge", "not_selected", "selected", "selected", "not_selected"],
            ["12:00"],
        ),
        (
            ["selected", "selected", "not_selected", "edge", "not_selected"],
            ["00:00"],
        ),
        (
            ["selected", "selected", "not_selected", "selected", "selected"],
            ["00:00", "18:00"],
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
            [
                "00:00", "00:30", "01:00", "01:30",
                "02:00", "02:30", "03:00", "03:30",
                "04:00", "04:30", "05:00", "05:30",
                "06:00", "06:30", "07:00", "07:30",
                "08:00", "08:30", "09:00", "09:30",
                "10:00", "10:30", "11:00", "11:30",
                "12:00", "12:30", "13:00", "13:30",
                "14:00", "14:30", "15:00", "15:30",
                "16:00", "16:30", "17:00", "17:30",
                "18:00", "18:30", "19:00", "19:30",
                "20:00", "20:30", "21:00", "21:30",
                "22:00", "22:30", "23:00", "23:30",
            ],
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
            [
                "00:00",
                "02:00", "02:30",
                "04:00", "04:30", "05:00", "05:30",
                "06:00",
                "16:00", "16:30", "17:00", "17:30",
                "18:00", "18:30", "19:00", "19:30",
                "20:00", "20:30", "21:00", "21:30",
                "22:00", "22:30", "23:00", "23:30",
            ],
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
            [
                "08:00", "08:30", "09:00", "09:30",
                "10:00", "10:30", "11:00", "11:30",
                "13:00", "13:30",
                "14:00", "14:30", "15:00", "15:30",
                "16:00", "16:30"
            ],
        ),
    ],
)
def test_get_selected_times(times_statuses, expected_result):
    result = get_selected_times(times_statuses)
    assert result == expected_result


@pytest.mark.parametrize(
    "times_statuses,expected_result",
    [
        (
            ["not_selected", "not_selected", "not_selected", "not_selected"],
            "<b>Выберите рабочие часы:</b>",
        ),
        (
            ["edge", "not_selected", "not_selected", "not_selected"],
            "<b>Выбранные рабочие часы:</b>\n00:00-...",
        ),
        (
            ["not_selected", "not_selected", "not_selected", "edge"],
            "<b>Выбранные рабочие часы:</b>\n...-00:00",
        ),
        (
            ["not_selected", "edge", "not_selected", "not_selected"],
            "<b>Выбранные рабочие часы:</b>\n...-08:00-...",
        ),
        (
            ["selected", "selected", "selected"],
            "<b>Выбранные рабочие часы:</b>\n00:00-00:00",
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            "<b>Выбранные рабочие часы:</b>\n00:00-00:00",
        ),
        (
            ["edge", "not_selected", "selected", "selected", "not_selected"],
            "<b>Выбранные рабочие часы:</b>\n00:00-...\n12:00-18:00",
        ),
        (
            ["selected", "selected", "not_selected", "edge", "not_selected"],
            "<b>Выбранные рабочие часы:</b>\n00:00-06:00\n...-18:00-...",
        ),
        (
            ["selected", "selected", "not_selected", "selected", "selected"],
            "<b>Выбранные рабочие часы:</b>\n00:00-06:00\n18:00-00:00",
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
            "<b>Выбранные рабочие часы:</b>\n00:00-00:00",
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
            "<b>Выбранные рабочие часы:</b>\n00:00-00:30\n02:00-03:00\n04:00-06:30\n16:00-00:00",
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
            "<b>Выбранные рабочие часы:</b>\n08:00-12:00\n13:00-17:00",
        ),
    ],
)
def test_get_times_statuses_view(times_statuses, expected_result):
    assert get_times_statuses_view(times_statuses) == expected_result


@pytest.mark.parametrize(
    "iso_dates,iso_times,expected_result",
    [
        (
            ["2025-02-15", "2025-02-22", "2026-04-10"],
            ["00:30", "10:00", "10:30", "16:30"],
            {
                "2025-02-14": ["2025-02-14T21:30:00"],
                "2025-02-15": ["2025-02-15T07:00:00", "2025-02-15T07:30:00", "2025-02-15T13:30:00"],
                "2025-02-21": ["2025-02-21T21:30:00"],
                "2025-02-22": ["2025-02-22T07:00:00", "2025-02-22T07:30:00", "2025-02-22T13:30:00"],
                "2026-04-09": ["2026-04-09T21:30:00"],
                "2026-04-10": ["2026-04-10T07:00:00", "2026-04-10T07:30:00", "2026-04-10T13:30:00"],
            },
        ),
    ],
)
def test_get_slots_to_save(iso_dates, iso_times, expected_result):
    result = get_slots_to_save(iso_dates, iso_times)
    assert result == expected_result


@pytest.mark.parametrize(
    "iso_dates,iso_times,expected_result",
    [
        (
            ["2025-02-15", "2025-02-22", "2026-04-10"],
            ["00:30", "10:00", "10:30", "16:30"],
            [
                "2025-02-14T21:30:00", "2025-02-15T07:00:00", "2025-02-15T07:30:00",
                "2025-02-15T13:30:00", "2025-02-21T21:30:00", "2025-02-22T07:00:00",
                "2025-02-22T07:30:00", "2025-02-22T13:30:00", "2026-04-09T21:30:00",
                "2026-04-10T07:00:00", "2026-04-10T07:30:00", "2026-04-10T13:30:00",
            ],
        ),
    ],
)
def test_get_slots_to_delete(iso_dates, iso_times, expected_result):
    result = get_slots_to_delete(iso_dates, iso_times)
    assert result == expected_result


@pytest.mark.parametrize(
    "iso_times,duration_multiplier,expected_result",
    [
        (["10:00"], 30, "10:00-10:30"),
        (["00:00"], 30, "00:00-00:30"),
        (["23:30"], 30, "23:30-00:00"),
        (["10:00", "10:30", "11:00", "11:30"], 30, "10:00-12:00"),
        (["10:00", "15:00"], 30, "10:00-10:30\n15:00-15:30"),
        (["10:00", "10:30", "15:00", "15:30"], 30, "10:00-11:00\n15:00-16:00"),
        (["15:30", "10:00", "15:00", "10:30"], 30, "10:00-11:00\n15:00-16:00"),
        (["10:00"], 15, "10:00-10:15"),
        (["10:00", "10:15", "10:30", "10:45"], 15, "10:00-11:00"),
        (["10:00", "15:00"], 15, "10:00-10:15\n15:00-15:15"),
        (["10:00", "11:00", "15:00", "16:00"], 60, "10:00-12:00\n15:00-17:00"),
        (["16:00", "10:00", "15:00", "11:00"], 60, "10:00-12:00\n15:00-17:00"),
        (
            ["15:00", "09:30", "22:30", "11:30", "06:00"],
            30,
            "06:00-06:30\n09:30-10:00\n11:30-12:00\n15:00-15:30\n22:30-23:00",
        ),
    ],
)
def test_get_working_hours_view(iso_times, duration_multiplier, expected_result):
    result = get_working_hours_view(iso_times, duration_multiplier)
    assert result == expected_result


@pytest.mark.parametrize(
    "times_statuses,clicked_element,expected_result",
    [
        (
            ["not_selected", "not_selected", "not_selected"],
            1,
            ["edge", "not_selected", "not_selected"],
        ),
        (
            ["not_selected", "not_selected", "not_selected"],
            2,
            ["not_selected", "edge", "not_selected"],
        ),
        (
            ["not_selected", "not_selected", "not_selected"],
            3,
            ["not_selected", "not_selected", "edge"],
        ),
        (
            ["not_selected", "not_selected", "edge"],
            1,
            ["selected", "selected", "selected"],
        ),
        (
            ["not_selected", "not_selected", "edge"],
            2,
            ["not_selected", "selected", "selected"],
        ),
        (
            ["not_selected", "not_selected", "edge"],
            3,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["not_selected", "edge", "not_selected"],
            1,
            ["selected", "selected", "not_selected"],
        ),
        (
            ["not_selected", "edge", "not_selected"],
            2,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["not_selected", "edge", "not_selected"],
            3,
            ["not_selected", "selected", "selected"],
        ),
        (
            ["not_selected", "selected", "selected"],
            1,
            ["selected", "selected", "selected"],
        ),
        (
            ["not_selected", "selected", "selected"],
            2,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["not_selected", "selected", "selected"],
            3,
            ["not_selected", "edge", "not_selected"],
        ),
        (
            ["edge", "not_selected", "not_selected"],
            1,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["edge", "not_selected", "not_selected"],
            2,
            ["selected", "selected", "not_selected"],
        ),
        (
            ["edge", "not_selected", "not_selected"],
            3,
            ["selected", "selected", "selected"],
        ),
        (
            ["selected", "selected", "not_selected"],
            1,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "not_selected"],
            2,
            ["edge", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "not_selected"],
            3,
            ["selected", "selected", "selected"],
        ),
        (
            ["selected", "selected", "selected"],
            1,
            ["not_selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected"],
            2,
            ["edge", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected"],
            3,
            ["selected", "selected", "not_selected"],
        ),
        (
            [
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            3,
            [
                "not_selected", "not_selected",
                "edge", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
        ),
        (
            [
                "not_selected", "not_selected",
                "edge", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            6,
            [
                "not_selected", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
        ),
        (
            [
                "not_selected", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            1,
            [
                "edge", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
        ),
        (
            [
                "edge", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            4,
            [
                "selected", "selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
        ),
        (
            [
                "edge", "not_selected",
                "selected", "selected",
                "selected", "selected",
                "not_selected", "not_selected",
                "not_selected", "not_selected",
            ],
            10,
            [
                "selected", "selected",
                "selected", "selected",
                "selected", "selected",
                "selected", "selected",
                "selected", "selected",
            ],
        ),
        (
            ["not_selected", "not_selected", "not_selected", "edge", "not_selected"],
            2,
            ["not_selected", "selected", "selected", "selected", "not_selected"],
        ),
        (
            ["selected", "selected", "not_selected", "edge", "not_selected"],
            2,
            ["selected", "selected", "selected", "selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            5,
            ["selected", "selected", "selected", "selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            4,
            ["selected", "selected", "selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            3,
            ["selected", "selected", "not_selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            2,
            ["edge", "not_selected", "not_selected", "not_selected", "not_selected"],
        ),
        (
            ["selected", "selected", "selected", "selected", "selected"],
            1,
            ["not_selected", "not_selected", "not_selected", "not_selected", "not_selected"],
        ),
    ],
)
def test_resolve_times_statuses(
    times_statuses,
    clicked_element,
    expected_result,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.stuff.schedule.utils.TIMES_STATUSES_LEN", len(times_statuses))
    clicked_index = clicked_element - 1
    assert resolve_times_statuses(times_statuses, clicked_index) == expected_result


@pytest.mark.parametrize(
    "times_statuses",
    [
        ["not_selected", "not_selected", "selected"],
        ["not_selected", "edge", "edge"],
        ["not_selected", "edge", "selected"],
        ["not_selected", "selected", "not_selected"],
        ["not_selected", "selected", "edge"],
        ["edge", "not_selected", "edge"],
        ["edge", "not_selected", "selected"],
        ["edge", "edge", "not_selected"],
        ["edge", "edge", "edge"],
        ["edge", "edge", "selected"],
        ["edge", "selected", "not_selected"],
        ["edge", "selected", "edge"],
        ["edge", "selected", "selected"],
        ["selected", "not_selected", "not_selected"],
        ["selected", "not_selected", "edge"],
        ["selected", "not_selected", "selected"],
        ["selected", "edge", "not_selected"],
        ["selected", "edge", "edge"],
        ["selected", "edge", "selected"],
        ["selected", "selected", "edge"],
        ["not_selected", "finish", "not_selected"],
        ["selected", "selected", "selected", "selected"],
    ],
)
def test_resolve_times_statuses_raises_assertion_error(
    times_statuses,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr("src.stuff.schedule.utils.TIMES_STATUSES_LEN", 3)
    with pytest.raises(AssertionError):
        resolve_times_statuses(times_statuses, clicked_index=1)
