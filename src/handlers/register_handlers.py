from aiogram import Dispatcher, F
from aiogram.enums import ChatType

from src.handlers.handlers import (
    choose_day_for_appointment,
    choose_month_for_appointment,
    choose_time_for_appointment,
    choose_service_field_to_update,
    choose_service_to_delete,
    choose_service_to_update,
    choose_service_for_appointment,
    choose_services_action,
    choose_year_for_appointment,
    choose_appointments_action,
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
from src.keyboards import USLUGI, ZAPISI
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
    dp.message.register(
        choose_year_for_appointment,
        F.chat.id != ADMIN_TG_ID,
        MakeAppointment.choose_year,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_month_for_appointment,
        F.chat.id != ADMIN_TG_ID,
        MakeAppointment.choose_month,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_day_for_appointment,
        F.chat.id != ADMIN_TG_ID,
        MakeAppointment.choose_day,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_time_for_appointment,
        F.chat.id != ADMIN_TG_ID,
        MakeAppointment.choose_time,
        F.chat.type == ChatType.PRIVATE.value,
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
