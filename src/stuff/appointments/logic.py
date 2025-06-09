from datetime import datetime, time, timedelta
from aiogram import types
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src import messages
from src.config import TIMEZONE
from src.database import (
    get_active_appointments,
    get_available_slots,
    get_services,
    insert_appointment,
    insert_reservations,
)
from src.models import Appointment
from src.secrets import ADMIN_TG_ID
from src.stuff.appointments.exceptions import (
    DateTimeBecomeNotAvailable,
    DayBecomeNotAvailable,
    MonthBecomeNotAvailable,
    YearBecomeNotAvailable,
)
from src.stuff.appointments.keyboards import (
    SHOW_ACTIVE_ZAPISI,
    ZAPIS_NA_PRIEM,
    AppointmentDateTimePicker,
    appointments_keyboard,
    get_confirm_appointment_keyboard,
    get_days_keyboard,
    get_months_keyboard,
    get_times_keyboard,
    get_years_keyboard,
)
from src.stuff.appointments.states import MakeAppointment
from src.stuff.appointments.utils import (
    check_chosen_datetime_is_possible,
    get_datetimes_needed_for_appointment,
    get_days_keyboard_buttons,
    get_months_keyboard_buttons,
    get_times_keyboard_buttons,
    get_times_possible_for_appointment,
    get_years_keyboard_buttons,
)
from src.stuff.base.logic import LogicResult, MessageToAnswer, MessageToSend, get_logic_result
from src.stuff.common.keyboards import BACK, MAIN_MENU, back_main_keyboard
from src.stuff.common.logic import show_services, to_main_menu_result
from src.stuff.common.utils import (
    dates_to_lang,
    form_appointment_view,
    form_appointments_list_text,
    from_utc,
    get_utc_now,
    get_years_with_months,
    get_years_with_months_days,
    to_utc,
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


def go_to_choose_year_for_appointment_logic(
    state_data: dict,
) -> LogicResult:
    times_dict = state_data["times_dict"]
    years = list(times_dict.keys())
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    years_keyboard_buttons = get_years_keyboard_buttons(years, tz_now)
    years_keyboard = get_years_keyboard(years_keyboard_buttons)
    state_to_set = MakeAppointment.choose_year
    edit_message = MessageToAnswer(messages.CHOOSE_YEAR, years_keyboard)
    return get_logic_result(state_to_set=state_to_set, edit_message=edit_message)


def go_to_choose_month_for_appointment_logic(
    state_data: dict,
    callback_data: AppointmentDateTimePicker,
) -> LogicResult:
    times_dict = state_data["times_dict"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    years_with_months = get_years_with_months(times_dict)
    months_keyboard_buttons = get_months_keyboard_buttons(
        years_with_months,
        tz_now,
        chosen_year,
    )
    keyboard = get_months_keyboard(chosen_year, months_keyboard_buttons)
    state_to_set = MakeAppointment.choose_month
    edit_message = MessageToAnswer(messages.CHOOSE_MONTH, keyboard)
    return get_logic_result(state_to_set=state_to_set, edit_message=edit_message)


def go_to_choose_day_for_appointment_logic(
    state_data: dict,
    callback_data: AppointmentDateTimePicker,
) -> LogicResult:
    times_dict = state_data["times_dict"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    chosen_month = callback_data.month
    years_with_months_days = get_years_with_months_days(times_dict)
    days_keyboard_buttons = get_days_keyboard_buttons(
        years_with_months_days,
        tz_now,
        chosen_year,
        chosen_month,
    )
    keyboard = get_days_keyboard(chosen_year, chosen_month, days_keyboard_buttons)
    state_to_set = MakeAppointment.choose_day
    edit_message = MessageToAnswer(messages.CHOOSE_DAY, keyboard)
    return get_logic_result(state_to_set=state_to_set, edit_message=edit_message)


def go_to_choose_time_for_appointment_logic(
    state_data: dict,
    callback_data: AppointmentDateTimePicker,
) -> LogicResult:
    times_dict = state_data["times_dict"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    chosen_month = callback_data.month
    chosen_day = callback_data.day
    times_keyboard_buttons = get_times_keyboard_buttons(
        times_dict,
        tz_now,
        chosen_year,
        chosen_month,
        chosen_day,
    )
    keyboard = get_times_keyboard(
        chosen_year,
        chosen_month,
        chosen_day,
        times_keyboard_buttons,
    )
    state_to_set = MakeAppointment.choose_time
    edit_message = MessageToAnswer(messages.CHOOSE_TIME, keyboard)
    return get_logic_result(state_to_set=state_to_set, edit_message=edit_message)


def go_to_confirm_appointment_logic(
    state_data: dict,
    callback_data: AppointmentDateTimePicker,
) -> LogicResult:
    chosen_service_name = state_data["chosen_service_name"]
    chosen_year = callback_data.year
    chosen_month = callback_data.month
    chosen_day = callback_data.day
    chosen_time = time.fromisoformat(callback_data.time)
    chosen_datetime = datetime(
        chosen_year,
        chosen_month,
        chosen_day,
        chosen_time.hour,
        chosen_time.minute,
    )
    keyboard = get_confirm_appointment_keyboard(chosen_datetime)
    state_to_set = MakeAppointment.confirm
    edit_message = MessageToAnswer(
        messages.CONFIRM_APPOINTMENT.format(
            lang_day_month_year=dates_to_lang(chosen_year, chosen_month, chosen_day),
            time=chosen_time.isoformat(timespec="minutes"),
            service_name=chosen_service_name,
        ),
        keyboard,
    )
    return get_logic_result(state_to_set=state_to_set, edit_message=edit_message)


async def appointment_confirmed_logic(
    callback: types.CallbackQuery,
    state_data: dict,
    callback_data: AppointmentDateTimePicker,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    chosen_service_name = state_data["chosen_service_name"]
    async with async_session() as session:
        [chosen_service] = await get_services(session, filter_by={"name": chosen_service_name})
    chosen_year = callback_data.year
    chosen_month = callback_data.month
    chosen_day = callback_data.day
    chosen_time = time.fromisoformat(callback_data.time)
    tz_starts_at = TIMEZONE.localize(
        datetime(
            chosen_year,
            chosen_month,
            chosen_day,
            chosen_time.hour,
            chosen_time.minute,
        )
    )
    starts_at = to_utc(tz_starts_at)
    ends_at = starts_at + timedelta(minutes=chosen_service.duration)
    appointment = Appointment(
        client_id=callback.from_user.id,
        service_id=chosen_service.service_id,
        starts_at=starts_at,
        ends_at=ends_at,
    )
    datetimes_to_reserve = get_datetimes_needed_for_appointment(starts_at, chosen_service.duration)
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    async with async_session() as session:
        try:
            await insert_appointment(session, appointment)
            await session.flush()
            await insert_reservations(session, datetimes_to_reserve, appointment.appointment_id)
            await session.flush()
        except IntegrityError:
            await session.rollback()
            slots = await get_available_slots(session, utc_now)
            times_dict = await get_times_possible_for_appointment(chosen_service, slots)
            if not times_dict:
                data_to_set = {}
                state_to_set = MakeAppointment.choose_action
                messages_to_answer = [
                    MessageToAnswer(
                        messages.NO_POSSIBLE_TIMES_FOR_SERVICE,
                        appointments_keyboard,
                    ),
                ]
                return get_logic_result(
                    messages_to_answer=messages_to_answer,
                    state_to_set=state_to_set,
                    data_to_set=data_to_set,
                )
            data_to_update = {"times_dict": times_dict}
            try:
                check_chosen_datetime_is_possible(tz_starts_at, times_dict)
            except DateTimeBecomeNotAvailable as err:
                if isinstance(err, YearBecomeNotAvailable):
                    state_to_set = MakeAppointment.choose_year
                    message_to_edit_to = messages.CHOOSE_YEAR
                    years = list(times_dict.keys())
                    years_keyboard_buttons = get_years_keyboard_buttons(years, tz_now)
                    keyboard_to_show = get_years_keyboard(years_keyboard_buttons)
                elif isinstance(err, MonthBecomeNotAvailable):
                    state_to_set = MakeAppointment.choose_month
                    message_to_edit_to = messages.CHOOSE_MONTH
                    years_with_months = get_years_with_months(times_dict)
                    months_keyboard_buttons = get_months_keyboard_buttons(
                        years_with_months,
                        tz_now,
                        chosen_year,
                    )
                    keyboard_to_show = get_months_keyboard(chosen_year, months_keyboard_buttons)
                elif isinstance(err, DayBecomeNotAvailable):
                    state_to_set = MakeAppointment.choose_day
                    message_to_edit_to = messages.CHOOSE_DAY
                    years_with_months_days = get_years_with_months_days(times_dict)
                    days_keyboard_buttons = get_days_keyboard_buttons(
                        years_with_months_days,
                        tz_now,
                        chosen_year,
                        chosen_month,
                    )
                    keyboard_to_show = get_days_keyboard(
                        chosen_year,
                        chosen_month,
                        days_keyboard_buttons,
                    )
                else:
                    state_to_set = MakeAppointment.choose_time
                    message_to_edit_to = messages.CHOOSE_TIME
                    times_keyboard_buttons = get_times_keyboard_buttons(
                        times_dict,
                        tz_now,
                        chosen_year,
                        chosen_month,
                        chosen_day,
                    )
                    keyboard_to_show = get_times_keyboard(
                        chosen_year,
                        chosen_month,
                        chosen_day,
                        times_keyboard_buttons,
                    )
                edit_message = MessageToAnswer(message_to_edit_to, keyboard_to_show)
                alert_text = str(err)
                return get_logic_result(
                    state_to_set=state_to_set,
                    data_to_update=data_to_update,
                    edit_message=edit_message,
                    alert_text=alert_text,
                )
            else:
                assert False
        else:
            await session.refresh(appointment)
            text_to_answer = (
                f"{messages.APPOINTMENT_SAVED}\n"
                f"{messages.COME.format(appointment_view=form_appointment_view(appointment, with_date=True, for_admin=False))}"
            )
            messages_to_answer = [ MessageToAnswer(text_to_answer, appointments_keyboard) ]
            await session.commit()
            messages_to_send = [
                MessageToSend(
                    ADMIN_TG_ID,
                    messages.NEW_APPOINTMENT_CREATED.format(
                        appointment_view=form_appointment_view(appointment, with_date=True, for_admin=True),
                    ),
                ),
            ]
            data_to_set = {}
            state_to_set = MakeAppointment.choose_action
            alert_text = messages.APPOINTMENT_SAVED
            return get_logic_result(
                messages_to_answer=messages_to_answer,
                state_to_set=state_to_set,
                data_to_set=data_to_set,
                messages_to_send=messages_to_send,
                alert_text=alert_text,
            )


def cancel_choose_date_for_appointment_logic() -> LogicResult:
    messages_to_answer = [ MessageToAnswer(messages.CANCELED, appointments_keyboard) ]
    data_to_set = {}
    state_to_set = MakeAppointment.choose_action
    return get_logic_result(
        messages_to_answer=messages_to_answer,
        state_to_set=state_to_set,
        data_to_set=data_to_set,
    )
