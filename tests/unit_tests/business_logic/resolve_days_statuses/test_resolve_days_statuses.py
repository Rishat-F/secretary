import pytest

from src.business_logic.resolve_days_statuses.resolve_days_statuses import resolve_days_statuses


@pytest.mark.parametrize(
    "days_statuses,clicked_element,expected_result",
    [
    # all group clicked
        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "not_selected_all",
            [
                "selected_all", "selected_monday", "selected_tuesday", "selected_wednesday", "selected_thursday", "selected_friday", "selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "selected_5", "selected_6", "selected_7", "selected_8", "selected_9",
                "selected_week3", "selected_10", "selected_11", "selected_12", "selected_13", "selected_14", "selected_15", "selected_16",
                "selected_week4", "selected_17", "selected_18", "selected_19", "selected_20", "selected_21", "selected_22", "selected_23",
                "selected_week5", "selected_24", "selected_25", "selected_26", "selected_27", "selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "selected_monday", "selected_tuesday", "selected_wednesday", "selected_thursday", "selected_friday", "selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "selected_5", "selected_6", "selected_7", "selected_8", "selected_9",
                "selected_week3", "selected_10", "selected_11", "selected_12", "selected_13", "selected_14", "selected_15", "selected_16",
                "selected_week4", "selected_17", "selected_18", "selected_19", "selected_20", "selected_21", "selected_22", "selected_23",
                "selected_week5", "selected_24", "selected_25", "selected_26", "selected_27", "selected_28", "ignore", "ignore",
            ],
            "selected_all",
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "selected_7", "not_selected_8", "selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "selected_all",
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

    # day clicked
        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "not_selected_7",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "selected_7",
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "selected_7",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "selected_7", "not_selected_8", "selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "selected_7",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "selected_7", "not_selected_8", "selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "selected_7",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

    # day of week group clicked
        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "not_selected_thursday",
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "not_selected_monday",
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "selected_week3", "selected_10", "not_selected_11", "not_selected_12", "selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "selected_17", "not_selected_18", "not_selected_19", "selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "selected_week5", "selected_24", "not_selected_25", "not_selected_26", "selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "selected_week3", "selected_10", "not_selected_11", "not_selected_12", "selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "selected_17", "not_selected_18", "not_selected_19", "selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "selected_week5", "selected_24", "not_selected_25", "not_selected_26", "selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "not_selected_friday",
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "selected_6", "selected_7", "not_selected_8", "not_selected_9",
                "selected_week3", "selected_10", "not_selected_11", "not_selected_12", "selected_13", "selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "selected_17", "not_selected_18", "not_selected_19", "selected_20", "selected_21", "not_selected_22", "not_selected_23",
                "selected_week5", "selected_24", "not_selected_25", "not_selected_26", "selected_27", "selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "selected_6", "selected_7", "not_selected_8", "not_selected_9",
                "selected_week3", "selected_10", "not_selected_11", "not_selected_12", "selected_13", "selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "selected_17", "not_selected_18", "not_selected_19", "selected_20", "selected_21", "not_selected_22", "not_selected_23",
                "selected_week5", "selected_24", "not_selected_25", "not_selected_26", "selected_27", "selected_28", "ignore", "ignore",
            ],
            "selected_thursday",
            [
                "selected_all", "selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "selected_7", "not_selected_8", "not_selected_9",
                "selected_week3", "selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "selected_14", "not_selected_15", "not_selected_16",
                "selected_week4", "selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "selected_21", "not_selected_22", "not_selected_23",
                "selected_week5", "selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "selected_28", "ignore", "ignore",
            ],
        ),

    # week group clicked
        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "not_selected_week3",
            [
                "selected_all", "selected_monday", "selected_tuesday", "selected_wednesday", "selected_thursday", "selected_friday", "selected_saturday", "selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "selected_week3", "selected_10", "selected_11", "selected_12", "selected_13", "selected_14", "selected_15", "selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
        ),

        (
            [
                "not_selected_all", "not_selected_monday", "not_selected_tuesday", "not_selected_wednesday", "not_selected_thursday", "not_selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "not_selected_week5", "not_selected_24", "not_selected_25", "not_selected_26", "not_selected_27", "not_selected_28", "ignore", "ignore",
            ],
            "not_selected_week5",
            [
                "selected_all", "selected_monday", "selected_tuesday", "selected_wednesday", "selected_thursday", "selected_friday", "not_selected_saturday", "not_selected_sunday",
                "not_available_week1", "ignore", "ignore", "ignore", "ignore", "ignore", "not_available_1", "not_available_2",
                "not_selected_week2", "not_available_3", "not_available_4", "not_selected_5", "not_selected_6", "not_selected_7", "not_selected_8", "not_selected_9",
                "not_selected_week3", "not_selected_10", "not_selected_11", "not_selected_12", "not_selected_13", "not_selected_14", "not_selected_15", "not_selected_16",
                "not_selected_week4", "not_selected_17", "not_selected_18", "not_selected_19", "not_selected_20", "not_selected_21", "not_selected_22", "not_selected_23",
                "selected_week5", "selected_24", "selected_25", "selected_26", "selected_27", "selected_28", "ignore", "ignore",
            ],
        ),
    ],
)
def test_resolve_days_statuses(days_statuses, clicked_element, expected_result):
    assert resolve_days_statuses(days_statuses, clicked_element) == expected_result
