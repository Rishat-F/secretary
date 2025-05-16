from aiogram import Dispatcher, F
from aiogram.enums import ChatType
from aiogram.filters import or_f

from src.business_logic.resolve_days_statuses.utils import ScheduleDayStatus
from src.handlers.handlers import (
    alert_not_available_to_choose,
    alert_not_available_to_choose_day,
    appointment_confirmed,
    cancel_choose_date_for_appointment,
    choose_service_field_to_update,
    choose_service_to_delete,
    choose_service_to_update,
    choose_service_for_appointment,
    choose_services_action,
    choose_appointments_action,
    clear_schedule_clicked,
    clear_schedule_confirmed,
    day_clicked,
    delete_schedule,
    go_to_choose_day_for_appointment,
    go_to_choose_day_while_view_schedule,
    go_to_choose_month_for_appointment,
    go_to_choose_month_for_set_schedule,
    go_to_choose_month_while_view_schedule,
    go_to_choose_time_for_appointment,
    show_working_hours,
    go_to_choose_year_for_appointment,
    go_to_choose_year_for_set_schedule,
    go_to_choose_year_while_view_schedule,
    go_to_confirm_appointment,
    go_to_main_menu_from_schedule,
    go_to_set_working_days,
    go_to_set_working_hours,
    ignore_inline_button,
    save_schedule,
    schedule,
    schedule_modifying,
    set_service_duration,
    set_service_name,
    set_service_new_duration,
    set_service_new_name,
    set_service_new_price,
    set_service_price,
    start_bot,
    services,
    appointments,
    time_clicked,
)
from src.keyboards import SCHEDULE, USLUGI, ZAPISI, AppointmentDateTimePicker, Schedule
from src.secrets import ADMIN_TG_ID
from src.states import ServicesActions, MakeAppointment, ScheduleStates


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков."""
    dp.message.register(
        choose_appointments_action,
        F.chat.id != ADMIN_TG_ID,
        MakeAppointment.choose_action,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_service_for_appointment,
        F.chat.id != ADMIN_TG_ID,
        MakeAppointment.choose_service,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.callback_query.register(
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
    dp.callback_query.register(
        ignore_inline_button,
        or_f(
            AppointmentDateTimePicker.filter(F.action == "ignore"),
            Schedule.filter(F.action == "ignore"),
        ),
    )
    dp.callback_query.register(
        go_to_choose_year_for_appointment,
        or_f(
            MakeAppointment.choose_month,
            MakeAppointment.choose_day,
            MakeAppointment.choose_time,
        ),
        AppointmentDateTimePicker.filter(F.action == "choose_year"),
    )
    dp.callback_query.register(
        go_to_choose_month_for_appointment,
        or_f(
            MakeAppointment.choose_year,
            MakeAppointment.choose_day,
            MakeAppointment.choose_time,
        ),
        AppointmentDateTimePicker.filter(F.action == "choose_month"),
    )
    dp.callback_query.register(
        go_to_choose_day_for_appointment,
        or_f(
            MakeAppointment.choose_month,
            MakeAppointment.choose_time,
        ),
        AppointmentDateTimePicker.filter(F.action == "choose_day"),
    )
    dp.callback_query.register(
        go_to_choose_time_for_appointment,
        or_f(
            MakeAppointment.choose_day,
            MakeAppointment.confirm,
        ),
        AppointmentDateTimePicker.filter(F.action == "choose_time"),
    )
    dp.callback_query.register(
        go_to_confirm_appointment,
        MakeAppointment.choose_time,
        AppointmentDateTimePicker.filter(F.action == "confirm"),
    )
    dp.callback_query.register(
        appointment_confirmed,
        MakeAppointment.confirm,
        AppointmentDateTimePicker.filter(F.action == "confirmed"),
    )
    dp.callback_query.register(
        alert_not_available_to_choose,
        or_f(
            MakeAppointment.choose_year,
            MakeAppointment.choose_month,
            MakeAppointment.choose_day,
        ),
        AppointmentDateTimePicker.filter(F.action == "not_available"),
    )
    dp.message.register(
        choose_services_action,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.choose_action,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_service_name,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.set_name,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_service_price,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.set_price,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_service_duration,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.set_duration,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_service_to_delete,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.choose_service_to_delete,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_service_to_update,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.choose_service_to_update,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_service_field_to_update,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.choose_service_field_to_update,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_service_new_name,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.set_new_name,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_service_new_price,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.set_new_price,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_service_new_duration,
        F.chat.id == ADMIN_TG_ID,
        ServicesActions.set_new_duration,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        start_bot,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower().contains("/start"),
    )
    dp.message.register(
        services,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower() == USLUGI.lower(),
    )
    dp.message.register(
        appointments,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower() == ZAPISI.lower(),
    )
    dp.message.register(
        schedule,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower() == SCHEDULE.lower(),
    )
    dp.callback_query.register(
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
    dp.callback_query.register(
        go_to_choose_year_while_view_schedule,
        ScheduleStates.view_schedule,
        Schedule.filter(F.action == "choose_year"),
    )
    dp.callback_query.register(
        go_to_choose_month_while_view_schedule,
        ScheduleStates.view_schedule,
        Schedule.filter(F.action == "choose_month"),
    )
    dp.callback_query.register(
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
    dp.callback_query.register(
        show_working_hours,
        ScheduleStates.view_schedule,
        Schedule.filter(F.action == "choose_time"),
    )
    dp.callback_query.register(
        schedule_modifying,
        ScheduleStates.view_schedule,
        Schedule.filter(F.action == "modify_schedule"),
    )
    dp.callback_query.register(
        clear_schedule_clicked,
        ScheduleStates.view_schedule,
        Schedule.filter(F.action == "clear_schedule"),
    )
    dp.callback_query.register(
        clear_schedule_confirmed,
        ScheduleStates.confirm_schedule_clear,
        Schedule.filter(F.action == "clear_schedule_confirmed"),
    )
    dp.callback_query.register(
        go_to_choose_year_for_set_schedule,
        or_f(
            ScheduleStates.choose_month,
            ScheduleStates.set_working_days,
        ),
        Schedule.filter(F.action == "choose_year"),
    )
    dp.callback_query.register(
        go_to_choose_month_for_set_schedule,
        or_f(
            ScheduleStates.choose_year,
            ScheduleStates.set_working_days,
        ),
        Schedule.filter(F.action == "choose_month"),
    )
    dp.callback_query.register(
        go_to_set_working_days,
        or_f(
            ScheduleStates.choose_month,
            ScheduleStates.set_working_hours,
        ),
        Schedule.filter(F.action == "choose_day"),
    )
    dp.callback_query.register(
        go_to_set_working_hours,
        or_f(
            ScheduleStates.choose_year,
            ScheduleStates.choose_month,
            ScheduleStates.set_working_days,
        ),
        Schedule.filter(F.action == "set_time"),
    )
    dp.callback_query.register(
        save_schedule,
        or_f(
            ScheduleStates.choose_year,
            ScheduleStates.choose_month,
            ScheduleStates.set_working_days,
            ScheduleStates.set_working_hours,
        ),
        Schedule.filter(F.action == "save"),
    )
    dp.callback_query.register(
        delete_schedule,
        or_f(
            ScheduleStates.choose_year,
            ScheduleStates.choose_month,
            ScheduleStates.set_working_days,
            ScheduleStates.set_working_hours,
        ),
        Schedule.filter(F.action == "delete"),
    )
    dp.callback_query.register(
        time_clicked,
        ScheduleStates.set_working_hours,
        Schedule.filter(F.action == "time_clicked"),
    )
    dp.callback_query.register(
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
    dp.callback_query.register(
        alert_not_available_to_choose_day,
        ScheduleStates.set_working_days,
        Schedule.filter(F.action == ScheduleDayStatus.NOT_AVAILABLE),
    )
