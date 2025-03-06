"""Конечные автоматы состояний."""

from aiogram.fsm.state import State, StatesGroup


class UslugiActions(StatesGroup):
    """Конечный автомат состояний управления услугами."""

    choose_action = State()
    set_name = State()
    set_price = State()
    set_duration = State()
