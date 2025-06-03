from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.schedule.get_schedule import get_schedule
from src.business_logic.schedule.utils import view_schedule_get_days_keyboard_buttons
from src import messages
from src.config import TIMEZONE
from src.database import get_future_slots, get_services, get_active_appointments
from src.secrets import ADMIN_TG_ID

from src.stuff.appointments.keyboards import appointments_keyboard
from src.stuff.appointments.states import MakeAppointment
from src.stuff.common.logic import LogicResult, MessageToAnswer, get_logic_result, show_services
from src.stuff.common.utils import (
    form_appointments_list_text,
    from_utc,
    get_utc_now,
    get_years_with_months_days,
)
from src.stuff.main_menu.keyboards import get_main_keyboard
from src.stuff.schedule.keyboards import view_schedule_get_days_keyboard
from src.stuff.schedule.states import ScheduleStates
from src.stuff.services.keyboards import services_keyboard
from src.stuff.services.states import ServicesActions


async def services_logic(user_id: int, session: AsyncSession) -> LogicResult:
    if user_id == ADMIN_TG_ID:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, services_keyboard) ]
        state_to_set = ServicesActions.choose_action
        return get_logic_result(messages_to_answer, state_to_set)
    else:
        services = await get_services(session)
        main_keyboard = get_main_keyboard(for_admin=False)
        message_to_send = show_services(services, main_keyboard, show_duration=False)
        messages_to_answer = [message_to_send]
        return get_logic_result(messages_to_answer)


async def appointments_logic(user_id: int, session: AsyncSession) -> LogicResult:
    if user_id == ADMIN_TG_ID:
        utc_now = get_utc_now()
        appointments = await get_active_appointments(session, utc_now)
        text = form_appointments_list_text(appointments, for_admin=True)
        main_keyboard = get_main_keyboard(for_admin=True)
        messages_to_answer = [ MessageToAnswer(text, main_keyboard) ]
        return get_logic_result(messages_to_answer)
    else:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, appointments_keyboard) ]
        state_to_set = MakeAppointment.choose_action
        return get_logic_result(messages_to_answer, state_to_set)


async def schedule_logic(
    session: AsyncSession,
) -> LogicResult:
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    slots = await get_future_slots(session, utc_now)
    schedule_dict = get_schedule(slots)
    state_to_set = ScheduleStates.view_schedule
    data_to_set = {"schedule_dict": schedule_dict}
    messages_to_answer = [
        MessageToAnswer(
            messages.SCHEDULE,
            types.ReplyKeyboardRemove(),
        ),
    ]
    if not schedule_dict:
        messages_to_answer.append(
            MessageToAnswer(
                messages.NO_SCHEDULE,
                view_schedule_get_days_keyboard(0, 0, []),
            ),
        )
        return get_logic_result(messages_to_answer, state_to_set)
    else:
        years_with_months_days = get_years_with_months_days(schedule_dict)
        chosen_year = min(years_with_months_days.keys())
        chosen_month = min(years_with_months_days[chosen_year].keys())
        days_to_choose = view_schedule_get_days_keyboard_buttons(
            years_with_months_days,
            tz_now,
            chosen_year,
            chosen_month,
        )
        messages_to_answer.append(
            MessageToAnswer(
                messages.SCHEDULE_VIEW,
                view_schedule_get_days_keyboard(chosen_year, chosen_month, days_to_choose),
            )
        )
        return get_logic_result(messages_to_answer, state_to_set, data_to_set)
