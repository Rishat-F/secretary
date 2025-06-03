from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from src import messages
from src.config import TIMEZONE
from src.database import get_active_appointments, get_available_slots, get_services
from src.stuff.appointments.keyboards import (
    SHOW_ACTIVE_ZAPISI,
    ZAPIS_NA_PRIEM,
    appointments_keyboard,
    get_days_keyboard,
)
from src.stuff.appointments.states import MakeAppointment
from src.stuff.appointments.utils import (
    get_days_keyboard_buttons,
    get_times_possible_for_appointment,
)
from src.stuff.common.keyboards import BACK, MAIN_MENU, back_main_keyboard
from src.stuff.common.logic import (
    LogicResult,
    MessageToAnswer,
    get_logic_result,
    show_services,
    to_main_menu_result,
)
from src.stuff.common.utils import (
    form_appointments_list_text,
    from_utc,
    get_utc_now,
    get_years_with_months_days,
)


async def choose_appointments_action_logic(
    user_input: str,
    user_id: int,
    session: AsyncSession,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        return to_main_menu_result(is_admin=False)
    elif upper_text == ZAPIS_NA_PRIEM.upper():
        services = await get_services(session)
        if not services:
            messages_to_answer = [ MessageToAnswer(messages.NO_SERVICES, appointments_keyboard) ]
            return get_logic_result(messages_to_answer)
        else:
            services_for_appointment = {str(pos): service.name for pos, service in enumerate(services, start=1)}
            message_to_send_1 = show_services(services, back_main_keyboard, show_duration=False)
            message_to_send_2 = MessageToAnswer(messages.CHOOSE_SERVICE_TO_MAKE_APPOINTMENT, back_main_keyboard)
            messages_to_answer = [message_to_send_1, message_to_send_2]
            state_to_set = MakeAppointment.choose_service
            data_to_set = {"services_for_appointment": services_for_appointment}
            return get_logic_result(messages_to_answer, state_to_set, data_to_set)
    elif upper_text == SHOW_ACTIVE_ZAPISI.upper():
        utc_now = get_utc_now()
        appointments = await get_active_appointments(session, utc_now, filter_by={"client_id": user_id})
        text = form_appointments_list_text(appointments, for_admin=False)
        messages_to_answer = [ MessageToAnswer(text, appointments_keyboard) ]
        return get_logic_result(messages_to_answer)
    else:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_GIVEN_ACTION, appointments_keyboard) ]
        return get_logic_result(messages_to_answer)


async def choose_service_for_appointment_logic(
    user_input: str,
    state_data: dict,
    session: AsyncSession,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, appointments_keyboard) ]
        state_to_set = MakeAppointment.choose_action
        return get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return to_main_menu_result(is_admin=False)
    else:
        services_for_appointment = state_data["services_for_appointment"]
        pos_for_appointment = text
        service_name_for_appointment = services_for_appointment.get(pos_for_appointment)
        if service_name_for_appointment is None:
            messages_to_answer = [ MessageToAnswer(messages.CHOOSE_SERVICE_TO_MAKE_APPOINTMENT, back_main_keyboard) ]
            return get_logic_result(messages_to_answer)
        else:
            services = await get_services(session, filter_by={"name": service_name_for_appointment})
            if not services:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.NO_SUCH_SERVICE.format(name=service_name_for_appointment),
                        back_main_keyboard,
                    ),
                ]
                return get_logic_result(messages_to_answer)
            [service] = services
            utc_now = get_utc_now()
            tz_now = from_utc(utc_now, TIMEZONE)
            slots = await get_available_slots(session, utc_now)
            times_dict = await get_times_possible_for_appointment(service, slots)
            if not times_dict:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.NO_POSSIBLE_TIMES_FOR_SERVICE.format(name=service.name),
                        back_main_keyboard,
                    ),
                ]
                return get_logic_result(messages_to_answer)
            else:
                years_with_months_days = get_years_with_months_days(times_dict)
                chosen_year = min(years_with_months_days.keys())
                chosen_month = min(years_with_months_days[chosen_year].keys())
                days_to_choose = get_days_keyboard_buttons(
                    years_with_months_days,
                    tz_now,
                    chosen_year,
                    chosen_month,
                )
                messages_to_answer = [
                    MessageToAnswer(
                        messages.MAKING_APPOINTMENT.format(service_name=service_name_for_appointment),
                        types.ReplyKeyboardRemove(),
                    ),
                    MessageToAnswer(
                        messages.CHOOSE_DATE,
                        get_days_keyboard(chosen_year, chosen_month, days_to_choose),
                    ),
                ]
                state_to_set = MakeAppointment.choose_day
                data_to_set = {
                    "chosen_service_name": service.name,
                    "times_dict": times_dict,
                }
                return get_logic_result(messages_to_answer, state_to_set, data_to_set)
