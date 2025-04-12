from aiogram import Dispatcher, F
from aiogram.enums import ChatType
from aiogram.filters import or_f

from src.handlers.handlers import (
    alert_not_available_to_choose,
    appointment_confirmed,
    cancel_choose_date_for_appointment,
    choose_service_field_to_update,
    choose_service_to_delete,
    choose_service_to_update,
    choose_service_for_appointment,
    choose_services_action,
    choose_appointments_action,
    go_to_choose_day_for_appointment,
    go_to_choose_month_for_appointment,
    go_to_choose_time_for_appointment,
    go_to_choose_year_for_appointment,
    go_to_confirm_appointment,
    ignore_inline_button,
    set_service_duration,
    set_service_name,
    set_service_new_duration,
    set_service_new_name,
    set_service_new_price,
    set_service_price,
    start_bot,
    services,
    appointments,
)
from src.keyboards import USLUGI, ZAPISI, DateTimePicker
from src.secrets import ADMIN_TG_ID
from src.states import ServicesActions, MakeAppointment


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
        DateTimePicker.filter(F.action == "cancel"),
    )
    dp.callback_query.register(
        ignore_inline_button,
        DateTimePicker.filter(F.action == "ignore"),
    )
    dp.callback_query.register(
        go_to_choose_year_for_appointment,
        or_f(
            MakeAppointment.choose_month,
            MakeAppointment.choose_day,
            MakeAppointment.choose_time,
        ),
        DateTimePicker.filter(F.action == "choose_year"),
    )
    dp.callback_query.register(
        go_to_choose_month_for_appointment,
        or_f(
            MakeAppointment.choose_year,
            MakeAppointment.choose_day,
            MakeAppointment.choose_time,
        ),
        DateTimePicker.filter(F.action == "choose_month"),
    )
    dp.callback_query.register(
        go_to_choose_day_for_appointment,
        or_f(
            MakeAppointment.choose_month,
            MakeAppointment.choose_time,
        ),
        DateTimePicker.filter(F.action == "choose_day"),
    )
    dp.callback_query.register(
        go_to_choose_time_for_appointment,
        or_f(
            MakeAppointment.choose_day,
            MakeAppointment.confirm,
        ),
        DateTimePicker.filter(F.action == "choose_time"),
    )
    dp.callback_query.register(
        go_to_confirm_appointment,
        MakeAppointment.choose_time,
        DateTimePicker.filter(F.action == "confirm"),
    )
    dp.callback_query.register(
        appointment_confirmed,
        MakeAppointment.confirm,
        DateTimePicker.filter(F.action == "confirmed"),
    )
    dp.callback_query.register(
        alert_not_available_to_choose,
        or_f(
            MakeAppointment.choose_year,
            MakeAppointment.choose_month,
            MakeAppointment.choose_day,
        ),
        DateTimePicker.filter(F.action == "not_available"),
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
