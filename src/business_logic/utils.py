from src.constraints import DURATION_MULTIPLIER


def _get_times_statuses_len(duration_multiplier: int) -> int:
    times_statuses_len = (24 * 60) // duration_multiplier + 1
    return times_statuses_len


TIMES_STATUSES_LEN = _get_times_statuses_len(DURATION_MULTIPLIER)
MINIMAL_TIMES_STATUSES_LEN = 3


class ScheduleTimeStatus:
    NOT_SELECTED = "not_selected"
    SELECTED = "selected"
    EDGE = "edge"


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
