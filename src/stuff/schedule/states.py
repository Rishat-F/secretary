from aiogram.fsm.state import State, StatesGroup


class ScheduleStates(StatesGroup):
    """Конечный автомат состояний управления графиком работы."""

    view_schedule = State()
    confirm_schedule_clear = State()
    choose_year = State()
    choose_month = State()
    set_working_days = State()
    set_working_hours = State()
