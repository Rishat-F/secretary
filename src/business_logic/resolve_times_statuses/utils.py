from datetime import date, datetime, time

from src import messages
from src.business_logic.schedule.utils import MINIMAL_ALL_TIMES_LEN, get_all_times_len
from src.config import TIMEZONE
from src.constraints import DURATION_MULTIPLIER
from src.keyboards import InlineButton
from src.utils import to_utc


TIMES_STATUSES_LEN = get_all_times_len(DURATION_MULTIPLIER)
MINIMAL_TIMES_STATUSES_LEN = MINIMAL_ALL_TIMES_LEN


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
    Проверка отсутствия невозможных сценариев для times_statuses.

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


def _get_duration_multiplier_by_times_statuses(times_statuses_len: int) -> int:
    assert times_statuses_len >= MINIMAL_TIMES_STATUSES_LEN
    duration_multiplier = 24*60/(times_statuses_len - 1)
    return int(duration_multiplier)


def _get_iso_time_from_time_index(index: int, duration_multiplier: int) -> str:
    total_minutes = index * duration_multiplier
    hours = (total_minutes // 60) % 24
    minutes = total_minutes % 60
    time_ = time(hours, minutes)
    return time_.isoformat(timespec="minutes")


def get_selected_times(times_statuses: list[str]) -> list[str]:
    selected_iso_times = []
    duration_multiplier = _get_duration_multiplier_by_times_statuses(len(times_statuses))
    for i in range(len(times_statuses)):
        current_element = times_statuses[i]
        try:
            next_element = times_statuses[i+1]
        except IndexError:
            next_element = None
        if (
            current_element == ScheduleTimeStatus.SELECTED
            and next_element == ScheduleTimeStatus.SELECTED
        ):
            iso_time = _get_iso_time_from_time_index(i, duration_multiplier)
            selected_iso_times.append(iso_time)
    return selected_iso_times


def get_times_statuses_view(times_statuses: list[str]) -> str:
    view = ""
    duration_multiplier = _get_duration_multiplier_by_times_statuses(len(times_statuses))
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
        view = messages.SET_WORKING_HOURS
    else:
        view = messages.SELECTED_WORKING_HOURS.format(selected_times_view=view)
    return view


def get_working_hours_view(iso_times: list[str], duration_multiplier: int) -> str:
    assert iso_times
    times = [time.fromisoformat(iso_time) for iso_time in iso_times]
    times = sorted(times)
    view = ""
    prev_element = None
    for i in range(len(times)):
        current_element = times[i]
        try:
            next_element = times[i+1]
        except IndexError:
            next_element = None
        if (
            prev_element is None
            or (
                (current_element.hour*60+current_element.minute) - (prev_element.hour*60+prev_element.minute)
            ) != duration_multiplier
        ):
            interval_start = current_element.isoformat(timespec="minutes")
            view += f"\n{interval_start}-"
        if (
            next_element is None
            or (
                (next_element.hour*60+next_element.minute) - (current_element.hour*60+current_element.minute)
            ) != duration_multiplier
        ):
            total_minutes = current_element.hour*60+current_element.minute
            interval_finish_minutes = total_minutes + duration_multiplier
            hours = (interval_finish_minutes // 60) % 24
            minutes = interval_finish_minutes % 60
            view += time(hours, minutes).isoformat(timespec="minutes")
        prev_element = times[i]
    view = view.strip()
    return view


def set_schedule_get_times_keyboard_buttons(times_statuses: list[str]) -> list[InlineButton]:
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


def get_slots_to_save(iso_tz_dates: list[str], iso_tz_times: list[str]) -> dict[str, list[str]]:
    assert iso_tz_dates
    assert iso_tz_times
    utc_slots: list[datetime] = []
    for iso_tz_date in iso_tz_dates:
        for iso_time in iso_tz_times:
            tz_date = date.fromisoformat(iso_tz_date)
            tz_time = time.fromisoformat(iso_time)
            slot_tz_dt = TIMEZONE.localize(datetime(tz_date.year, tz_date.month, tz_date.day, tz_time.hour, tz_time.minute))
            slot_utc_dt = to_utc(slot_tz_dt)
            utc_slots.append(slot_utc_dt)
    dates_slots = {}
    for utc_datetime in utc_slots:
        iso_date = utc_datetime.date().isoformat()
        iso_datetime = utc_datetime.replace(tzinfo=None).isoformat()
        if iso_date not in dates_slots:
            dates_slots[iso_date] = [iso_datetime]
        else:
            dates_slots[iso_date].append(iso_datetime)
    return dates_slots


def get_slots_to_delete(iso_tz_dates: list[str], iso_tz_times: list[str]) -> list[str]:
    assert iso_tz_dates
    assert iso_tz_times
    slots = []
    for iso_tz_date in iso_tz_dates:
        for iso_tz_time in iso_tz_times:
            tz_date = date.fromisoformat(iso_tz_date)
            tz_time = time.fromisoformat(iso_tz_time)
            slot_tz_dt = TIMEZONE.localize(datetime(tz_date.year, tz_date.month, tz_date.day, tz_time.hour, tz_time.minute))
            slot_utc_dt = to_utc(slot_tz_dt)
            iso_utc_datetime = slot_utc_dt.replace(tzinfo=None).isoformat()
            slots.append(iso_utc_datetime)
    return slots
