from aiogram.fsm.state import State, StatesGroup


class MakeAppointment(StatesGroup):
    """Конечный автомат состояний записи на прием."""

    choose_action = State()
    choose_service = State()
    choose_year = State()
    choose_month = State()
    choose_day = State()
    choose_time = State()
    confirm = State()
