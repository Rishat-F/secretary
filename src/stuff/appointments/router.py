from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import or_f

from src.secrets import ADMIN_TG_ID
from src.stuff.appointments.handlers import (
    appointment_confirmed,
    cancel_choose_date_for_appointment,
    choose_service_for_appointment,
    choose_appointments_action,
    go_to_choose_day_for_appointment,
    go_to_choose_month_for_appointment,
    go_to_choose_time_for_appointment,
    go_to_choose_year_for_appointment,
    go_to_confirm_appointment,
)
from src.stuff.appointments.keyboards import AppointmentDateTimePicker
from src.stuff.appointments.states import MakeAppointment


router = Router()


router.message.register(
    choose_appointments_action,
    F.chat.id != ADMIN_TG_ID,
    MakeAppointment.choose_action,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    choose_service_for_appointment,
    F.chat.id != ADMIN_TG_ID,
    MakeAppointment.choose_service,
    F.chat.type == ChatType.PRIVATE.value,
)
router.callback_query.register(
    cancel_choose_date_for_appointment,
    or_f(
        MakeAppointment.choose_year,
        MakeAppointment.choose_month,
        MakeAppointment.choose_day,
        MakeAppointment.choose_time,
        MakeAppointment.confirm,
    ),
    AppointmentDateTimePicker.filter(F.action == "cancel"),
)
router.callback_query.register(
    go_to_choose_year_for_appointment,
    or_f(
        MakeAppointment.choose_month,
        MakeAppointment.choose_day,
        MakeAppointment.choose_time,
    ),
    AppointmentDateTimePicker.filter(F.action == "choose_year"),
)
router.callback_query.register(
    go_to_choose_month_for_appointment,
    or_f(
        MakeAppointment.choose_year,
        MakeAppointment.choose_day,
        MakeAppointment.choose_time,
    ),
    AppointmentDateTimePicker.filter(F.action == "choose_month"),
)
router.callback_query.register(
    go_to_choose_day_for_appointment,
    or_f(
        MakeAppointment.choose_month,
        MakeAppointment.choose_time,
    ),
    AppointmentDateTimePicker.filter(F.action == "choose_day"),
)
router.callback_query.register(
    go_to_choose_time_for_appointment,
    or_f(
        MakeAppointment.choose_day,
        MakeAppointment.confirm,
    ),
    AppointmentDateTimePicker.filter(F.action == "choose_time"),
)
router.callback_query.register(
    go_to_confirm_appointment,
    MakeAppointment.choose_time,
    AppointmentDateTimePicker.filter(F.action == "confirm"),
)
router.callback_query.register(
    appointment_confirmed,
    MakeAppointment.confirm,
    AppointmentDateTimePicker.filter(F.action == "confirmed"),
)
