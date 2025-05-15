import pytest

from src.business_logic.resolve_days_statuses.resolve_days_statuses import resolve_days_statuses


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
