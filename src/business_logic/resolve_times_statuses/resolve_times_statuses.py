from src.business_logic.resolve_times_statuses.utils import (
    ScheduleTimeStatus,
    check_clicked_index_assertions,
    check_times_statuses_assertions,
)


def resolve_times_statuses(times_statuses: list[str], clicked_index: int) -> list[str]:
    """Выбор диапазонов рабочего времени."""
    check_times_statuses_assertions(times_statuses)
    check_clicked_index_assertions(clicked_index)
    prev_index = clicked_index - 1
    prev_prev_index = clicked_index - 2
    next_index = clicked_index + 1
    if ScheduleTimeStatus.EDGE in times_statuses:
        edge_index = times_statuses.index(ScheduleTimeStatus.EDGE)
        if clicked_index < edge_index:
            for i in range(clicked_index, edge_index + 1):
                times_statuses[i] = ScheduleTimeStatus.SELECTED
        elif clicked_index == edge_index:
            times_statuses[edge_index] = ScheduleTimeStatus.NOT_SELECTED
        else:
            for i in range(edge_index, next_index):
                times_statuses[i] = ScheduleTimeStatus.SELECTED
    else:
        if times_statuses[clicked_index] == ScheduleTimeStatus.NOT_SELECTED:
            try:
                prev_status = times_statuses[prev_index]
            except IndexError:
                prev_status = None
            try:
                next_status = times_statuses[next_index]
            except IndexError:
                next_status = None
            if (
                prev_status == ScheduleTimeStatus.SELECTED
                or next_status == ScheduleTimeStatus.SELECTED
            ):
                times_statuses[clicked_index] = ScheduleTimeStatus.SELECTED
            else:
                times_statuses[clicked_index] = ScheduleTimeStatus.EDGE
        else:
            if prev_prev_index < 0:
                prev_prev_status = None
            else:
                prev_prev_status = times_statuses[prev_prev_index]
            if prev_index < 0:
                prev_status = None
            else:
                prev_status = times_statuses[prev_index]
            if prev_status != ScheduleTimeStatus.SELECTED:
                for i in range(clicked_index, len(times_statuses)):
                    if times_statuses[i] != ScheduleTimeStatus.SELECTED:
                        break
                    times_statuses[i] = ScheduleTimeStatus.NOT_SELECTED
            else:
                for i in range(clicked_index, len(times_statuses)):
                    if times_statuses[i] != ScheduleTimeStatus.SELECTED:
                        break
                    times_statuses[i] = ScheduleTimeStatus.NOT_SELECTED
                if prev_prev_status != ScheduleTimeStatus.SELECTED:
                    times_statuses[prev_index] = ScheduleTimeStatus.EDGE
    check_times_statuses_assertions(times_statuses)
    return times_statuses
