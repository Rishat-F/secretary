from datetime import time

from src.constraints import DURATION_MULTIPLIER
from src.keyboards import InlineButton


def _get_times_statuses_len(duration_multiplier: int) -> int:
    times_statuses_len = (24 * 60) // duration_multiplier + 1
    return times_statuses_len


TIMES_STATUSES_LEN = _get_times_statuses_len(DURATION_MULTIPLIER)
MINIMAL_TIMES_STATUSES_LEN = 3


class ScheduleTimeStatus:
    NOT_SELECTED = "not_selected"
    SELECTED = "selected"
    EDGE = "edge"


def get_initial_times_statuses() -> list[str]:
    statuses_times = [ScheduleTimeStatus.NOT_SELECTED] * TIMES_STATUSES_LEN
    return statuses_times


def _no_isolated_selected(times_statuses: list[str]) -> bool:
    assert len(times_statuses) >= MINIMAL_TIMES_STATUSES_LEN
    if (
        times_statuses[0] == ScheduleTimeStatus.SELECTED
        and times_statuses[1] != ScheduleTimeStatus.SELECTED
    ) or (
        times_statuses[-1] == ScheduleTimeStatus.SELECTED
        and times_statuses[-2] != ScheduleTimeStatus.SELECTED
    ):
        return False
    for i in range(1, len(times_statuses) - 1):
        if (
            times_statuses[i] == ScheduleTimeStatus.SELECTED
            and times_statuses[i-1] != ScheduleTimeStatus.SELECTED
            and times_statuses[i+1] != ScheduleTimeStatus.SELECTED
        ):
            return False
    return True


def _no_edge_selected_combination(times_statuses: list[str]) -> bool:
    assert len(times_statuses) >= MINIMAL_TIMES_STATUSES_LEN
    for i in range(len(times_statuses) - 1):
        if (
            times_statuses[i] == ScheduleTimeStatus.EDGE
            and times_statuses[i+1] == ScheduleTimeStatus.SELECTED
        ):
            return False
    return True


def _no_selected_edge_combination(times_statuses: list[str]) -> bool:
    assert len(times_statuses) >= MINIMAL_TIMES_STATUSES_LEN
    for i in range(len(times_statuses) - 1):
        if (
            times_statuses[i] == ScheduleTimeStatus.SELECTED
            and times_statuses[i+1] == ScheduleTimeStatus.EDGE
        ):
            return False
    return True


def check_times_statuses_assertions(times_statuses: list[str]) -> None:
    """
    Проверка отсутствия невозможных сценариев для times_status.

    При наличии невозможного сценария вызывается AssertionError.
    """
    possible_statuses = [
        ScheduleTimeStatus.SELECTED,
        ScheduleTimeStatus.NOT_SELECTED,
        ScheduleTimeStatus.EDGE,
    ]
    assert len(times_statuses) == TIMES_STATUSES_LEN
    assert all([status in possible_statuses for status in times_statuses])
    assert times_statuses.count(ScheduleTimeStatus.EDGE) <= 1
    assert _no_isolated_selected(times_statuses)
    assert _no_edge_selected_combination(times_statuses)
    assert _no_selected_edge_combination(times_statuses)


def check_clicked_index_assertions(clicked_index: int) -> None:
    """
    Проверка отсутствия невозможных сценариев для clicked_index.

    При наличии невозможного сценария вызывается AssertionError.
    """
    assert clicked_index in range(TIMES_STATUSES_LEN)


def _get_duration_multiplier_by_times_statues(times_statuses_len: int) -> int:
    assert times_statuses_len >= MINIMAL_TIMES_STATUSES_LEN
    duration_multiplier = 24*60/(times_statuses_len - 1)
    return int(duration_multiplier)


def _get_iso_time_from_time_index(index: int, duration_multiplier: int) -> str:
    total_minutes = index * duration_multiplier
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    time_ = time(hours, minutes)
    return time_.isoformat(timespec="minutes")


def get_times_statuses_view(times_statuses: list[str]) -> str:
    view = ""
    duration_multiplier = _get_duration_multiplier_by_times_statues(len(times_statuses))
    prev_element = None
    for i in range(len(times_statuses)):
        current_element = times_statuses[i]
        try:
            next_element = times_statuses[i+1]
        except IndexError:
            next_element = None
        iso_time = _get_iso_time_from_time_index(i, duration_multiplier)
        if current_element == ScheduleTimeStatus.EDGE:
            view += "\n"
            if prev_element:
                view += "...-"
            view += iso_time
            if next_element:
                view += "-..."
        elif current_element == ScheduleTimeStatus.SELECTED:
            if prev_element != ScheduleTimeStatus.SELECTED:
                view += f"\n{iso_time}-"
            elif next_element != ScheduleTimeStatus.SELECTED:
                view += f"{iso_time}"
        prev_element = times_statuses[i]
    view = view.strip()
    if view == "":
        view = "Рабочие часы не выбраны"
    else:
        view = "Выбранные рабочие часы:\n" + view
    return view


def get_set_working_hours_keyboard_buttons(times_statuses: list[str]) -> list[InlineButton]:
    result = []
    for i in range(len(times_statuses)):
        iso_time = _get_iso_time_from_time_index(i, DURATION_MULTIPLIER)
        if times_statuses[i] == ScheduleTimeStatus.EDGE:
            text = "⚪️"
        elif times_statuses[i] == ScheduleTimeStatus.SELECTED:
            text = "✔️"
        else:
            text = iso_time
        result.append(InlineButton("time_clicked", text, value=str(i)))
    return result
