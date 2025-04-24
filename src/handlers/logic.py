from dataclasses import dataclass

from aiogram import types
from aiogram.fsm.state import State
from sqlalchemy.ext.asyncio import AsyncSession

from src.business_logic.resolve_days_statuses.utils import (
    get_initial_days_statuses,
    get_selected_days,
    get_selected_days_view,
    get_set_working_days_keyboard_buttons,
)
from src import messages
from src.config import TIMEZONE
from src.database import (
    delete_service,
    get_available_slots,
    get_services,
    get_active_appointments,
    insert_service,
    update_service,
)
from src.exceptions import ServiceNameTooLongError
from src.business_logic.make_appointment.get_times_possible_for_appointment import get_times_possible_for_appointment
from src.business_logic.make_appointment.utils import (
    get_days_keyboard_buttons,
    get_years_with_months_days,
)
from src.business_logic.resolve_times_statuses.utils import (
    get_initial_times_statuses,
    get_set_working_hours_keyboard_buttons,
    get_times_statuses_view,
)
from src.keyboards import (
    BACK,
    CREATE,
    DELETE,
    DURATION,
    MAIN_MENU,
    NAME,
    PRICE,
    SHOW_ACTIVE_ZAPISI,
    SHOW_ALL_USLUGI,
    UPDATE,
    UPDATE_ANOTHER_USLUGA,
    ZAPIS_NA_PRIEM,
    AppointmentDateTimePicker,
    back_main_keyboard,
    get_days_keyboard,
    get_services_to_update_keyboard,
    get_set_working_days_keyboard,
    get_set_working_hours_keyboard,
    main_keyboard,
    set_service_new_field_keyboard,
    service_fields_keyboard,
    services_keyboard,
    appointments_keyboard,
)
from src.models import Service
from src.secrets import ADMIN_TG_ID
from src.states import ServicesActions, MakeAppointment, SetSchedule
from src.utils import (
    date_to_lang,
    form_service_view,
    form_services_list_text,
    form_appointments_list_text,
    from_utc,
    get_utc_now,
    preprocess_text,
    validate_service_duration,
    validate_service_name,
    validate_service_price,
)


@dataclass
class MessageToAnswer:
    text: str
    keyboard: types.ReplyKeyboardMarkup | types.ReplyKeyboardRemove | types.InlineKeyboardMarkup


@dataclass
class MessageToSend:
    user_id: int
    text: str


@dataclass
class LogicResult:
    messages_to_answer: list[MessageToAnswer]
    state_to_set: State | None
    data_to_set: dict | None
    data_to_update: dict | None
    clear_state: bool
    messages_to_send: list[MessageToSend]


def _get_logic_result(
    messages_to_answer: list[MessageToAnswer],
    state_to_set: State | None = None,
    data_to_set: dict | None = None,
    data_to_update: dict | None = None,
    clear_state: bool = False,
    messages_to_send: list[MessageToSend] | None = None,
) -> LogicResult:
    if messages_to_send is None:
        messages_to_send = []
    logic_result = LogicResult(
        messages_to_answer,
        state_to_set,
        data_to_set,
        data_to_update,
        clear_state,
        messages_to_send,
    )
    return logic_result


def _to_main_menu_result(message_to_send: str = messages.MAIN_MENU) -> LogicResult:
    messages_to_answer = [ MessageToAnswer(message_to_send, main_keyboard) ]
    return _get_logic_result(messages_to_answer, clear_state=True)


def _show_services(
    services: list[Service],
    keyboard: types.ReplyKeyboardMarkup,
    show_duration: bool,
) -> MessageToAnswer:
    text = form_services_list_text(services, show_duration)
    message_to_send = MessageToAnswer(text, keyboard)
    return message_to_send


async def services_logic(user_id: int, session: AsyncSession) -> LogicResult:
    if user_id == ADMIN_TG_ID:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, services_keyboard) ]
        state_to_set = ServicesActions.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)
    else:
        services = await get_services(session)
        message_to_send = _show_services(services, main_keyboard, show_duration=False)
        messages_to_answer = [message_to_send]
        return _get_logic_result(messages_to_answer)


async def choose_services_action_logic(user_input: str, session: AsyncSession) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        return _to_main_menu_result()
    elif upper_text == SHOW_ALL_USLUGI.upper():
        services = await get_services(session)
        message_to_send = _show_services(services, services_keyboard, show_duration=True)
        messages_to_answer = [message_to_send]
        return _get_logic_result(messages_to_answer)
    elif upper_text == CREATE.upper():
        messages_to_answer = [ MessageToAnswer(messages.SET_SERVICE_NAME, back_main_keyboard) ]
        state_to_set = ServicesActions.set_name
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == UPDATE.upper():
        services = await get_services(session)
        if services:
            services_names = [service.name for service in services]
            data_to_set = {"services_names": services_names}
            state_to_set = ServicesActions.choose_service_to_update
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_SERVICE_TO_UPDATE,
                    get_services_to_update_keyboard(services_names),
                ),
            ]
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set)
        else:
            messages_to_answer = [ MessageToAnswer(messages.NO_SERVICES, services_keyboard) ]
            return _get_logic_result(messages_to_answer)
    elif upper_text == DELETE.upper():
        services = await get_services(session)
        if services:
            services_to_delete = {str(pos): service.name for pos, service in enumerate(services, start=1)}
            data_to_set = services_to_delete
            state_to_set = ServicesActions.choose_service_to_delete
            message_to_send_1 = _show_services(services, back_main_keyboard, show_duration=True)
            message_to_send_2 = MessageToAnswer(messages.CHOOSE_SERVICE_TO_DELETE, back_main_keyboard)
            messages_to_answer = [message_to_send_1, message_to_send_2]
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set)
        else:
            messages_to_answer = [ MessageToAnswer(messages.NO_SERVICES, services_keyboard) ]
            return _get_logic_result(messages_to_answer)
    else:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_GIVEN_ACTION, services_keyboard) ]
        return _get_logic_result(messages_to_answer)


async def set_service_name_logic(user_input: str, session: AsyncSession) -> LogicResult:
    text = preprocess_text(user_input)
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, services_keyboard) ]
        state_to_set = ServicesActions.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        try:
            service_name = validate_service_name(text)
        except ServiceNameTooLongError as err:
            messages_to_answer = [ MessageToAnswer(str(err), back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)
        else:
            services = await get_services(session, filter_by={"name": service_name})
            if services:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.SERVICE_ALREADY_EXISTS.format(name=service_name),
                        back_main_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer)
            else:
                messages_to_answer = [ MessageToAnswer(messages.SET_SERVICE_PRICE, back_main_keyboard) ]
                state_to_set = ServicesActions.set_price
                data_to_set = {"name": service_name}
                return _get_logic_result(messages_to_answer, state_to_set, data_to_set)


async def set_service_price_logic(user_input: str) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.SET_SERVICE_NAME, back_main_keyboard) ]
        state_to_set = ServicesActions.set_name
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        possible_price = validate_service_price(text)
        if isinstance(possible_price, int):
            messages_to_answer = [ MessageToAnswer(messages.SET_SERVICE_DURATION, back_main_keyboard) ]
            state_to_set = ServicesActions.set_duration
            data_to_update = {"price": possible_price}
            return _get_logic_result(messages_to_answer, state_to_set, data_to_update=data_to_update)
        else:
            error_message = possible_price
            messages_to_answer = [ MessageToAnswer(error_message, back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)


async def set_service_duration_logic(
    user_input: str,
    session: AsyncSession,
    state_data: dict,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.SET_SERVICE_PRICE, back_main_keyboard) ]
        state_to_set = ServicesActions.set_price
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        possible_duration = validate_service_duration(text)
        if isinstance(possible_duration, int):
            state_data.update({"duration": possible_duration})
            new_service = Service(**state_data)
            await insert_service(session, new_service)
            messages_to_answer = [
                MessageToAnswer(
                    messages.SERVICE_CREATED.format(name=new_service.name),
                    services_keyboard,
                ),
            ]
            state_to_set = ServicesActions.choose_action
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set={})
        else:
            error_message = possible_duration
            messages_to_answer = [ MessageToAnswer(error_message, back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)


async def choose_service_to_delete_logic(
    user_input: str,
    session: AsyncSession,
    services_to_delete: dict,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, services_keyboard) ]
        state_to_set = ServicesActions.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        pos_to_delete = text
        service_name_to_delete = services_to_delete.get(pos_to_delete)
        if service_name_to_delete is None:
            messages_to_answer = [ MessageToAnswer(messages.CHOOSE_SERVICE_TO_DELETE, back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)
        else:
            await delete_service(session, service_name_to_delete)
            messages_to_answer = [
                MessageToAnswer(
                    messages.SERVICE_DELETED.format(name=service_name_to_delete),
                    services_keyboard,
                ),
            ]
            state_to_set = ServicesActions.choose_action
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set={})


async def choose_service_to_update_logic(
    user_input: str,
    session: AsyncSession,
    services_names: list[str],
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, services_keyboard) ]
        state_to_set = ServicesActions.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif text in services_names:
        [chosen_service] = await get_services(session, filter_by={"name": text})
        answer = (
            f"{form_service_view(chosen_service, show_duration=True)}\n"
            f"{messages.CHOOSE_FIELD_TO_CHANGE}"
        )
        messages_to_answer = [ MessageToAnswer(answer, service_fields_keyboard) ]
        state_to_set = ServicesActions.choose_service_field_to_update
        data_to_update = {
            "chosen_service_name": chosen_service.name,
            "chosen_service_price": chosen_service.price,
            "chosen_service_duration": chosen_service.duration,
        }
        return _get_logic_result(messages_to_answer, state_to_set, data_to_update=data_to_update)
    else:
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_GIVEN_SERVICES,
                get_services_to_update_keyboard(services_names),
            )
        ]
        return _get_logic_result(messages_to_answer)


def _field_chosen_to_update(message_text: str, state_to_set: State) -> LogicResult:
    messages_to_answer = [ MessageToAnswer(message_text, set_service_new_field_keyboard) ]
    return _get_logic_result(messages_to_answer, state_to_set)


async def choose_service_field_to_update_logic(
    user_input: str,
    services_names: list[str],
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_SERVICE_TO_UPDATE,
                get_services_to_update_keyboard(services_names),
            ),
        ]
        state_to_set = ServicesActions.choose_service_to_update
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif upper_text in NAME.upper():
        return _field_chosen_to_update(
            message_text=messages.SET_SERVICE_NEW_NAME,
            state_to_set=ServicesActions.set_new_name,
        )
    elif upper_text in PRICE.upper():
        return _field_chosen_to_update(
            message_text=messages.SET_SERVICE_NEW_PRICE,
            state_to_set=ServicesActions.set_new_price,
        )
    elif upper_text in DURATION.upper():
        return _field_chosen_to_update(
            message_text=messages.SET_SERVICE_NEW_DURATION,
            state_to_set=ServicesActions.set_new_duration,
        )
    else:
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_GIVEN_FIELD_TO_CHANGE,
                service_fields_keyboard,
            ),
        ]
        return _get_logic_result(messages_to_answer)


def _back_from_changing_service_field(state_data: dict) -> LogicResult:
    chosen_service = Service(
        name=state_data["chosen_service_name"],
        price=state_data["chosen_service_price"],
        duration=state_data["chosen_service_duration"],
    )
    answer = (
        f"{form_service_view(chosen_service, show_duration=True)}\n"
        f"{messages.CHOOSE_FIELD_TO_CHANGE}"
    )
    messages_to_answer = [ MessageToAnswer(answer, service_fields_keyboard) ]
    state_to_set = ServicesActions.choose_service_field_to_update
    return _get_logic_result(messages_to_answer, state_to_set)


def _update_another_service(services_names: list[str]) -> LogicResult:
    state_to_set = ServicesActions.choose_service_to_update
    messages_to_answer = [
        MessageToAnswer(
            messages.CHOOSE_SERVICE_TO_UPDATE,
            get_services_to_update_keyboard(services_names),
        ),
    ]
    return _get_logic_result(messages_to_answer, state_to_set)


async def set_service_new_name_logic(
    user_input: str,
    session: AsyncSession,
    state_data: dict,
) -> LogicResult:
    text = preprocess_text(user_input)
    upper_text = text.upper()
    services_names: list = state_data["services_names"]
    if upper_text == BACK.upper():
        return _back_from_changing_service_field(state_data)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif upper_text == UPDATE_ANOTHER_USLUGA.upper():
        return _update_another_service(services_names)
    else:
        old_name = state_data["chosen_service_name"]
        if old_name == text:
            messages_to_answer = [
                MessageToAnswer(
                    messages.SERVICE_OLD_NAME_AND_NEW_NAME_ARE_SIMILAR,
                    set_service_new_field_keyboard,
                ),
            ]
            return _get_logic_result(messages_to_answer)
        else:
            try:
                new_name = validate_service_name(text)
            except ServiceNameTooLongError as err:
                messages_to_answer = [ MessageToAnswer(str(err), set_service_new_field_keyboard) ]
                return _get_logic_result(messages_to_answer)
            else:
                if new_name in services_names:
                    messages_to_answer = [
                        MessageToAnswer(
                            messages.SERVICE_ALREADY_EXISTS.format(name=new_name),
                            set_service_new_field_keyboard,
                        ),
                    ]
                    return _get_logic_result(messages_to_answer)
                else:
                    updated_services_names = [
                        new_name if name == old_name else name
                        for name in services_names
                    ]
                    await update_service(session, old_name, new_values={"name": new_name})
                    data_to_update = {
                        "services_names": updated_services_names,
                        "chosen_service_name": new_name,
                    }
                    messages_to_answer = [
                        MessageToAnswer(
                            messages.SERVICE_NEW_NAME_SETTLED.format(
                                old_name=old_name,
                                new_name=new_name,
                            ),
                            set_service_new_field_keyboard,
                        ),
                    ]
                    return _get_logic_result(messages_to_answer, data_to_update=data_to_update)


async def set_service_new_price_logic(
    user_input: str,
    session: AsyncSession,
    state_data: dict,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    services_names: list = state_data["services_names"]
    if upper_text == BACK.upper():
        return _back_from_changing_service_field(state_data)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif upper_text == UPDATE_ANOTHER_USLUGA.upper():
        return _update_another_service(services_names)
    else:
        possible_price = validate_service_price(text)
        if isinstance(possible_price, int):
            new_price = possible_price
            old_price = state_data["chosen_service_price"]
            if new_price == old_price:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.SERVICE_OLD_PRICE_AND_NEW_PRICE_ARE_SIMILAR,
                        set_service_new_field_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer)
            else:
                service_name = state_data["chosen_service_name"]
                await update_service(session, service_name, new_values={"price": new_price})
                data_to_update = {"chosen_service_price": new_price}
                messages_to_answer = [
                    MessageToAnswer(
                        messages.SERVICE_NEW_PRICE_SETTLED.format(
                            service_name=service_name,
                            old_price=old_price,
                            new_price=new_price,
                        ),
                        set_service_new_field_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer, data_to_update=data_to_update)
        else:
            error_message = possible_price
            messages_to_answer = [ MessageToAnswer(error_message, set_service_new_field_keyboard) ]
            return _get_logic_result(messages_to_answer)


async def set_service_new_duration_logic(
    user_input: str,
    session: AsyncSession,
    state_data: dict,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    services_names: list = state_data["services_names"]
    if upper_text == BACK.upper():
        return _back_from_changing_service_field(state_data)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif upper_text == UPDATE_ANOTHER_USLUGA.upper():
        return _update_another_service(services_names)
    else:
        possible_duration = validate_service_duration(text)
        if isinstance(possible_duration, int):
            new_duration = possible_duration
            old_duration = state_data["chosen_service_duration"]
            if new_duration == old_duration:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.SERVICE_OLD_DURATION_AND_NEW_DURATION_ARE_SIMILAR,
                        set_service_new_field_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer)
            else:
                service_name = state_data["chosen_service_name"]
                await update_service(session, service_name, new_values={"duration": new_duration})
                data_to_update = {"chosen_service_duration": new_duration}
                messages_to_answer = [
                    MessageToAnswer(
                        messages.SERVICE_NEW_DURATION_SETTLED.format(
                            service_name=service_name,
                            old_duration=old_duration,
                            new_duration=new_duration,
                        ),
                        set_service_new_field_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer, data_to_update=data_to_update)
        else:
            error_message = possible_duration
            messages_to_answer = [ MessageToAnswer(error_message, set_service_new_field_keyboard) ]
            return _get_logic_result(messages_to_answer)


async def appointments_logic(user_id: int, session: AsyncSession) -> LogicResult:
    if user_id == ADMIN_TG_ID:
        appointments = await get_active_appointments(session)
        text = form_appointments_list_text(appointments, for_admin=True)
        messages_to_answer = [ MessageToAnswer(text, main_keyboard) ]
        return _get_logic_result(messages_to_answer)
    else:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, appointments_keyboard) ]
        state_to_set = MakeAppointment.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)


async def choose_appointments_action_logic(
    user_input: str,
    user_id: int,
    session: AsyncSession,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        return _to_main_menu_result()
    elif upper_text == ZAPIS_NA_PRIEM.upper():
        services = await get_services(session)
        if not services:
            messages_to_answer = [ MessageToAnswer(messages.NO_SERVICES, appointments_keyboard) ]
            return _get_logic_result(messages_to_answer)
        else:
            services_for_appointment = {str(pos): service.name for pos, service in enumerate(services, start=1)}
            message_to_send_1 = _show_services(services, back_main_keyboard, show_duration=False)
            message_to_send_2 = MessageToAnswer(messages.CHOOSE_SERVICE_TO_MAKE_APPOINTMENT, back_main_keyboard)
            messages_to_answer = [message_to_send_1, message_to_send_2]
            state_to_set = MakeAppointment.choose_service
            data_to_set = {"services_for_appointment": services_for_appointment}
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set)
    elif upper_text == SHOW_ACTIVE_ZAPISI.upper():
        appointments = await get_active_appointments(session, filter_by={"client_id": user_id})
        text = form_appointments_list_text(appointments, for_admin=False)
        messages_to_answer = [ MessageToAnswer(text, appointments_keyboard) ]
        return _get_logic_result(messages_to_answer)
    else:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_GIVEN_ACTION, appointments_keyboard) ]
        return _get_logic_result(messages_to_answer)


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
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        services_for_appointment = state_data["services_for_appointment"]
        pos_for_appointment = text
        service_name_for_appointment = services_for_appointment.get(pos_for_appointment)
        if service_name_for_appointment is None:
            messages_to_answer = [ MessageToAnswer(messages.CHOOSE_SERVICE_TO_MAKE_APPOINTMENT, back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)
        else:
            services = await get_services(session, filter_by={"name": service_name_for_appointment})
            if not services:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.NO_SUCH_SERVICE.format(name=service_name_for_appointment),
                        back_main_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer)
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
                return _get_logic_result(messages_to_answer)
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
                return _get_logic_result(messages_to_answer, state_to_set, data_to_set)


def alert_not_available_to_choose_logic(callback_data: AppointmentDateTimePicker) -> str:
    alert_text = ""
    year = callback_data.year
    month = callback_data.month
    day = callback_data.day
    lang_date = date_to_lang(year, month, day)
    if year and month and callback_data.day:
        alert_text = messages.DAY_NOT_AVAILABLE.format(lang_day_month_year=lang_date)
    elif year and month:
        alert_text = messages.MONTH_NOT_AVAILABLE.format(lang_month_year=lang_date)
    else:
        alert_text = messages.YEAR_NOT_AVAILABLE.format(lang_year=lang_date)
    return alert_text


def schedule_logic() -> LogicResult:
    days_statuses = get_initial_days_statuses()
    selected_days = get_selected_days(days_statuses)
    days_statuses_view = get_selected_days_view(selected_days)
    set_working_days_keyboard_buttons = get_set_working_days_keyboard_buttons(
        days_statuses,
    )
    messages_to_answer = [
        MessageToAnswer(
            messages.SCHEDULE_DEFINING,
            types.ReplyKeyboardRemove(),
        ),
        MessageToAnswer(
            messages.SET_WORKING_DAYS.format(days_statuses_view=days_statuses_view),
            get_set_working_days_keyboard(set_working_days_keyboard_buttons),
        ),
    ]
    state_to_set = SetSchedule.set_working_days
    data_to_set = {"days_statuses": days_statuses}
    return _get_logic_result(messages_to_answer, state_to_set, data_to_set)
