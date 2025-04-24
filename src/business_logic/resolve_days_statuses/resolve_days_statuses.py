from src.business_logic.resolve_days_statuses.utils import (
    ScheduleDayGroup,
    ScheduleDayStatus,
    actualize_groups_selection_status,
    change_all_days_selection_status,
    change_day_of_week_days_selection_status,
    change_week_days_selection_status,
    check_days_statuses_assertions,
    check_clicked_element_assertions,
    is_day_of_week_element,
    is_week_element,
    split_element,
)


def resolve_days_statuses(days_statuses: list[str], clicked_element: str) -> list[str]:
    """Выбор диапазонов рабочих дней."""
    check_days_statuses_assertions(days_statuses)
    check_clicked_element_assertions(clicked_element, days_statuses)
    clicked_index = days_statuses.index(clicked_element)
    clicked_element_status, clicked_element_group_or_day = split_element(clicked_element)
    if clicked_element_status == ScheduleDayStatus.NOT_SELECTED:
        new_status = ScheduleDayStatus.SELECTED
    else:
        new_status = ScheduleDayStatus.NOT_SELECTED
    if clicked_element_group_or_day == ScheduleDayGroup.ALL:
        days_statuses = change_all_days_selection_status(days_statuses, new_status)
    elif is_day_of_week_element(clicked_element):
        days_statuses = change_day_of_week_days_selection_status(days_statuses, new_status, clicked_index)
    elif is_week_element(clicked_element):
        days_statuses = change_week_days_selection_status(days_statuses, new_status, clicked_index)
    else:
        _, day = split_element(clicked_element)
        days_statuses[clicked_index] = f"{new_status}{day}"
    days_statuses = actualize_groups_selection_status(days_statuses)
    check_days_statuses_assertions(days_statuses)
    return days_statuses
