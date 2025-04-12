"""Конечные автоматы состояний."""

from aiogram.fsm.state import State, StatesGroup


class ServicesActions(StatesGroup):
    """Конечный автомат состояний управления услугами."""

    choose_action = State()
    set_name = State()
    set_price = State()
    set_duration = State()
    choose_service_to_update = State()
    choose_service_field_to_update = State()
    set_new_name = State()
    set_new_price = State()
    set_new_duration = State()
    choose_service_to_delete = State()


class MakeAppointment(StatesGroup):
    """Конечный автомат состояний записи на прием."""

    choose_action = State()
    choose_service = State()
    choose_year = State()
    choose_month = State()
    choose_day = State()
    choose_time = State()
    confirm = State()
