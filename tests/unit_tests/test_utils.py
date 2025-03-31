import pytest

from src.utils import (
    _get_iso_time_from_slot_number,
    get_slot_number_from_time,
    get_slot_numbers_needed_for_appointment,
    get_times_for_appointment,
)


@pytest.mark.parametrize(
    "time_iso,expected_slot_number",
    [
        ("00:00", 1),
        ("00:01", 1),
        ("00:15", 1),
        ("00:29", 1),
        ("00:30", 2),
        ("00:31", 2),
        ("00:45", 2),
        ("00:59", 2),
        ("01:00", 3),
        ("01:01", 3),
        ("01:15", 3),
        ("01:29", 3),
        ("01:30", 4),
        ("01:31", 4),
        ("10:00", 21),
        ("10:00", 21),
        ("10:30", 22),
        ("23:00", 47),
        ("23:30", 48),
    ],
)
def test_get_slot_number_from_time(time_iso, expected_slot_number):
    assert get_slot_number_from_time(time_iso) == expected_slot_number


@pytest.mark.parametrize(
    "slot_number,expected_iso_time",
    [
        (1, "00:00"),
        (2, "00:30"),
        (3, "01:00"),
        (4, "01:30"),
        (5, "02:00"),
        (6, "02:30"),
        (45, "22:00"),
        (46, "22:30"),
        (47, "23:00"),
        (48, "23:30"),
    ],
)
def test__get_iso_time_from_slot_number(slot_number, expected_iso_time):
    assert _get_iso_time_from_slot_number(slot_number) == expected_iso_time


@pytest.mark.parametrize(
    "slots_ids_numbers,service_duration,expected_possible_times_with_slots_ids",
    [
        ([], 30, {}),
        ([], 90, {}),
        ([(1, 21)], 30, {"10:00": [1]}),
        ([(1, 21)], 60, {}),
        ([(1, 21), (2, 22)], 60, {"10:00": [1, 2]}),
        ([(1, 21), (2, 22), (3, 23)], 60, {"10:00": [1, 2], "10:30": [2, 3]}),
        ([(1, 21), (2, 22), (3, 23)], 30, {"10:00": [1], "10:30": [2], "11:00": [3]}),
        ([(1, 21), (2, 22), (3, 23)], 90, {"10:00": [1, 2, 3]}),
        ([(1, 21), (2, 22), (3, 23)], 120, {}),
        ([(1, 21), (2, 31), (3, 41)], 30, {"10:00": [1], "15:00": [2], "20:00": [3]}),
        ([(1, 21), (2, 31)], 60, {}),
        ([(1, 21), (2, 31), (3, 32), (4, 33), (5, 41), (6, 42)], 60, {"15:00": [2, 3], "15:30": [3, 4], "20:00": [5, 6]}),
    ],
)
def test_get_times_for_appointment(slots_ids_numbers, service_duration, expected_possible_times_with_slots_ids):
    assert get_times_for_appointment(slots_ids_numbers, service_duration) == expected_possible_times_with_slots_ids


@pytest.mark.parametrize(
    "start_slot_number,service_duration,expected_slots_numbers",
    [
        (21, 30, [21]),
        (21, 60, [21, 22]),
        (21, 90, [21, 22, 23]),
        (21, 120, [21, 22, 23, 24]),
    ],
)
def test_get_slot_numbers_needed_for_appointment(
    start_slot_number,
    service_duration,
    expected_slots_numbers,
):
    assert (
        get_slot_numbers_needed_for_appointment(start_slot_number, service_duration)
        == expected_slots_numbers
    )
