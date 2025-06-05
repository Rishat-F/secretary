from aiogram import F, Router
from aiogram.filters import or_f

from src.stuff.appointments.keyboards import AppointmentDateTimePicker
from src.stuff.appointments.states import MakeAppointment
from src.stuff.common.handlers import (
    alert_not_available_to_choose,
    emergency_returning_to_main_menu_from_inline_mode,
    emergency_returning_to_main_menu_from_reply_mode,
    ignore_inline_button,
)
from src.stuff.schedule.keyboards import Schedule
from src.stuff.schedule.states import ScheduleStates
from src.stuff.schedule.utils import ScheduleDayStatus


router = Router()

router.callback_query.register(
    ignore_inline_button,
    or_f(
        MakeAppointment.choose_year,
        MakeAppointment.choose_month,
        MakeAppointment.choose_day,
        ScheduleStates.view_schedule,
        ScheduleStates.set_working_days,
    ),
    or_f(
        AppointmentDateTimePicker.filter(F.action == "ignore"),
        Schedule.filter(F.action == "ignore"),
    ),
)
router.callback_query.register(
    alert_not_available_to_choose,
    or_f(
        MakeAppointment.choose_year,
        MakeAppointment.choose_month,
        MakeAppointment.choose_day,
        ScheduleStates.choose_month,
        ScheduleStates.set_working_days,
    ),
    or_f(
        AppointmentDateTimePicker.filter(F.action == "not_available"),
        Schedule.filter(F.action == ScheduleDayStatus.NOT_AVAILABLE),
    ),
)
router.message.register(emergency_returning_to_main_menu_from_reply_mode)  # данные обработчики должны регистрироваться последними!
router.callback_query.register(emergency_returning_to_main_menu_from_inline_mode)  # данные обработчики должны регистрироваться последними!
