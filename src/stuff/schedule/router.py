from aiogram import F, Router
from aiogram.filters import or_f

from src.stuff.schedule.handlers import (
    clear_schedule_clicked,
    clear_schedule_confirmed,
    day_clicked,
    delete_schedule,
    go_to_choose_day_while_view_schedule,
    go_to_choose_month_for_set_schedule,
    go_to_choose_month_while_view_schedule,
    show_working_hours,
    go_to_choose_year_for_set_schedule,
    go_to_choose_year_while_view_schedule,
    go_to_main_menu_from_schedule,
    go_to_set_working_days,
    go_to_set_working_hours,
    save_schedule,
    schedule_modifying,
    time_clicked,
)
from src.stuff.schedule.keyboards import Schedule
from src.stuff.schedule.states import ScheduleStates
from src.stuff.schedule.utils import ScheduleDayStatus


router = Router()

router.callback_query.register(
    go_to_main_menu_from_schedule,
    or_f(
        ScheduleStates.view_schedule,
        ScheduleStates.confirm_schedule_clear,
        ScheduleStates.choose_year,
        ScheduleStates.choose_month,
        ScheduleStates.set_working_days,
        ScheduleStates.set_working_hours,
    ),
    Schedule.filter(F.action == "main_menu"),
)
router.callback_query.register(
    go_to_choose_year_while_view_schedule,
    ScheduleStates.view_schedule,
    Schedule.filter(F.action == "choose_year"),
)
router.callback_query.register(
    go_to_choose_month_while_view_schedule,
    ScheduleStates.view_schedule,
    Schedule.filter(F.action == "choose_month"),
)
router.callback_query.register(
    go_to_choose_day_while_view_schedule,
    or_f(
        ScheduleStates.choose_year,
        ScheduleStates.choose_month,
        ScheduleStates.set_working_days,
        ScheduleStates.set_working_hours,
        ScheduleStates.confirm_schedule_clear,
        ScheduleStates.view_schedule,
    ),
    Schedule.filter(F.action == "view_schedule"),
)
router.callback_query.register(
    show_working_hours,
    ScheduleStates.view_schedule,
    Schedule.filter(F.action == "choose_time"),
)
router.callback_query.register(
    schedule_modifying,
    ScheduleStates.view_schedule,
    Schedule.filter(F.action == "modify_schedule"),
)
router.callback_query.register(
    clear_schedule_clicked,
    ScheduleStates.view_schedule,
    Schedule.filter(F.action == "clear_schedule"),
)
router.callback_query.register(
    clear_schedule_confirmed,
    ScheduleStates.confirm_schedule_clear,
    Schedule.filter(F.action == "clear_schedule_confirmed"),
)
router.callback_query.register(
    go_to_choose_year_for_set_schedule,
    or_f(
        ScheduleStates.choose_month,
        ScheduleStates.set_working_days,
    ),
    Schedule.filter(F.action == "choose_year"),
)
router.callback_query.register(
    go_to_choose_month_for_set_schedule,
    or_f(
        ScheduleStates.choose_year,
        ScheduleStates.set_working_days,
    ),
    Schedule.filter(F.action == "choose_month"),
)
router.callback_query.register(
    go_to_set_working_days,
    or_f(
        ScheduleStates.choose_month,
        ScheduleStates.set_working_hours,
    ),
    Schedule.filter(F.action == "choose_day"),
)
router.callback_query.register(
    go_to_set_working_hours,
    or_f(
        ScheduleStates.choose_year,
        ScheduleStates.choose_month,
        ScheduleStates.set_working_days,
    ),
    Schedule.filter(F.action == "set_time"),
)
router.callback_query.register(
    save_schedule,
    or_f(
        ScheduleStates.choose_year,
        ScheduleStates.choose_month,
        ScheduleStates.set_working_days,
        ScheduleStates.set_working_hours,
    ),
    Schedule.filter(F.action == "save"),
)
router.callback_query.register(
    delete_schedule,
    or_f(
        ScheduleStates.choose_year,
        ScheduleStates.choose_month,
        ScheduleStates.set_working_days,
        ScheduleStates.set_working_hours,
    ),
    Schedule.filter(F.action == "delete"),
)
router.callback_query.register(
    time_clicked,
    ScheduleStates.set_working_hours,
    Schedule.filter(F.action == "time_clicked"),
)
router.callback_query.register(
    day_clicked,
    ScheduleStates.set_working_days,
    Schedule.filter(
        F.action.in_(
            [
                ScheduleDayStatus.SELECTED,
                ScheduleDayStatus.NOT_SELECTED,
            ]
        )
    ),
)
