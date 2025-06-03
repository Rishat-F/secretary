from aiogram import F, Router
from aiogram.filters import or_f

from src.stuff.appointments.keyboards import AppointmentDateTimePicker
from src.stuff.appointments.states import MakeAppointment
from src.stuff.common.handlers import alert_not_available_to_choose, ignore_inline_button
from src.stuff.schedule.keyboards import Schedule
from src.stuff.schedule.states import ScheduleStates


router = Router()

router.callback_query.register(
    ignore_inline_button,
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
        ScheduleStates.set_working_days,
    ),
    or_f(
        AppointmentDateTimePicker.filter(F.action == "not_available"),
        Schedule.filter(F.action == "not_available"),
    ),
)
