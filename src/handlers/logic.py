from dataclasses import dataclass
from datetime import datetime, time, timedelta

from aiogram import types
from aiogram.fsm.state import State
from sqlalchemy.ext.asyncio import AsyncSession

from src import messages
from src.database import (
    delete_service,
    get_available_slots,
    get_services,
    get_active_appointments,
    insert_reservations,
    insert_service,
    insert_appointment,
    update_service,
)
from src.exceptions import ServiceNameTooLongError
from src.handlers.business_logic import get_times_possible_for_appointment
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
    back_main_keyboard,
    get_days_keyboard,
    get_months_keyboard,
    get_times_keyboard,
    get_services_to_update_keyboard,
    get_years_keyboard,
    main_keyboard,
    set_service_new_field_keyboard,
    service_fields_keyboard,
    services_keyboard,
    appointments_keyboard,
)
from src.models import Service, Appointment
from src.secrets import ADMIN_TG_ID
from src.states import ServicesActions, MakeAppointment
from src.utils import (
    form_service_view,
    form_services_list_text,
    form_appointment_view,
    form_appointments_list_text,
    get_slot_number_from_time,
    get_slots_ids_to_reserve,
    get_times,
    get_days,
    get_months,
    get_years,
    months_swapped,
    preprocess_text,
    validate_service_duration,
    validate_service_name,
    validate_service_price,
)


@dataclass
class MessageToAnswer:
    text: str
    keyboard: types.ReplyKeyboardMarkup


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
            now_ = datetime.now()
            current_date = now_.date()
            current_slot_number = get_slot_number_from_time(now_.time().isoformat(timespec="minutes"))
            slots = await get_available_slots(session, current_date, current_slot_number)
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
                years_to_choose = get_years(times_dict)
                messages_to_answer = [
                    MessageToAnswer(
                        messages.CHOOSE_YEAR,
                        get_years_keyboard(years_to_choose),
                    ),
                ]
                state_to_set = MakeAppointment.choose_year
                data_to_set = {
                    "chosen_service_name": service.name,
                    "years_to_choose": years_to_choose,
                    "times_dict": times_dict,
                }
                return _get_logic_result(messages_to_answer, state_to_set, data_to_set)


async def choose_year_for_appointment_logic(
    user_input: str,
    state_data: dict,
    session: AsyncSession,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        services = await get_services(session)
        if not services:
            return _to_main_menu_result(messages.NO_SERVICES)
        else:
            services_for_appointment = {str(pos): service.name for pos, service in enumerate(services, start=1)}
            message_to_send_1 = _show_services(services, back_main_keyboard, show_duration=False)
            message_to_send_2 = MessageToAnswer( messages.CHOOSE_SERVICE_TO_MAKE_APPOINTMENT, back_main_keyboard)
            messages_to_answer = [message_to_send_1, message_to_send_2]
            state_to_set = MakeAppointment.choose_service
            data_to_set = {"services_for_appointment": services_for_appointment}
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        years_to_choose = state_data["years_to_choose"]
        if text not in [str(year) for year in years_to_choose]:
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_GIVEN_YEAR,
                    get_years_keyboard(years_to_choose),
                ),
            ]
            return _get_logic_result(messages_to_answer)
        else:
            times_dict = state_data["times_dict"]
            chosen_year = int(text)
            months_to_choose = get_months(times_dict, chosen_year)
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_MONTH,
                    get_months_keyboard(months_to_choose),
                ),
            ]
            state_to_set = MakeAppointment.choose_month
            data_to_update = {
                "chosen_year": chosen_year,
                "months_to_choose": months_to_choose,
            }
            return _get_logic_result(
                messages_to_answer,
                state_to_set,
                data_to_update=data_to_update,
            )


async def choose_month_for_appointment_logic(user_input: str, state_data: dict) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        times_dict = state_data["times_dict"]
        years_to_choose = get_years(times_dict)
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_YEAR,
                get_years_keyboard(years_to_choose),
            ),
        ]
        state_to_set = MakeAppointment.choose_year
        data_to_update = {"years_to_choose": years_to_choose}
        return _get_logic_result(
            messages_to_answer,
            state_to_set,
            data_to_update=data_to_update,
        )
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        months_to_choose = state_data["months_to_choose"]
        if text not in months_to_choose:
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_GIVEN_MONTH,
                    get_months_keyboard(months_to_choose),
                ),
            ]
            return _get_logic_result(messages_to_answer)
        else:
            times_dict = state_data["times_dict"]
            chosen_year = state_data["chosen_year"]
            chosen_month = text
            days_to_choose = get_days(times_dict, chosen_year, chosen_month)
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_DAY,
                    get_days_keyboard(days_to_choose),
                ),
            ]
            state_to_set = MakeAppointment.choose_day
            data_to_update = {
                "chosen_month": chosen_month,
                "days_to_choose": days_to_choose,
            }
            return _get_logic_result(
                messages_to_answer,
                state_to_set,
                data_to_update=data_to_update,
            )


async def choose_day_for_appointment_logic(user_input: str, state_data: dict) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        times_dict = state_data["times_dict"]
        chosen_year = state_data["chosen_year"]
        months_to_choose = get_months(times_dict, chosen_year)
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_MONTH,
                get_months_keyboard(months_to_choose),
            ),
        ]
        state_to_set = MakeAppointment.choose_month
        data_to_update = {"months_to_choose": months_to_choose}
        return _get_logic_result(
            messages_to_answer,
            state_to_set,
            data_to_update=data_to_update,
        )
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        days_to_choose = state_data["days_to_choose"]
        if text not in [str(day) for day in days_to_choose]:
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_GIVEN_DAY,
                    get_days_keyboard(days_to_choose),
                ),
            ]
            return _get_logic_result(messages_to_answer)
        else:
            times_dict = state_data["times_dict"]
            chosen_year = state_data["chosen_year"]
            chosen_month = state_data["chosen_month"]
            chosen_day = int(text)
            times_to_choose = get_times(
                times_dict,
                chosen_year,
                chosen_month,
                chosen_day,
            )
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_TIME,
                    get_times_keyboard(times_to_choose),
                ),
            ]
            state_to_set = MakeAppointment.choose_time
            data_to_update = {
                "chosen_day": chosen_day,
                "times_to_choose": times_to_choose,
            }
            return _get_logic_result(
                messages_to_answer,
                state_to_set,
                data_to_update=data_to_update,
            )


async def choose_time_for_appointment_logic(
    user_input: str,
    user_id: int,
    state_data: dict,
    session: AsyncSession,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        times_dict = state_data["times_dict"]
        chosen_year = state_data["chosen_year"]
        chosen_month = state_data["chosen_month"]
        days_to_choose = get_days(times_dict, chosen_year, chosen_month)
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_DAY,
                get_days_keyboard(days_to_choose),
            ),
        ]
        state_to_set = MakeAppointment.choose_day
        data_to_update = {"days_to_choose": days_to_choose}
        return _get_logic_result(
            messages_to_answer,
            state_to_set,
            data_to_update=data_to_update,
        )
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        times_to_choose = state_data["times_to_choose"]
        if text not in times_to_choose:
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_GIVEN_TIME,
                    get_times_keyboard(times_to_choose),
                ),
            ]
            return _get_logic_result(messages_to_answer)
        else:
            times_dict = state_data["times_dict"]
            chosen_service_name = state_data["chosen_service_name"]
            [chosen_service] = await get_services(session, filter_by={"name": chosen_service_name})
            chosen_year = state_data["chosen_year"]
            chosen_month = months_swapped[state_data["chosen_month"]]
            chosen_day = state_data["chosen_day"]
            chosen_time = text
            start_time = time.fromisoformat(chosen_time)
            starts_at = datetime(
                chosen_year,
                chosen_month,
                chosen_day,
                start_time.hour,
                start_time.minute,
            )
            ends_at = starts_at + timedelta(minutes=chosen_service.duration)
            appointment = Appointment(
                client_id=user_id,
                service_id=chosen_service.service_id,
                starts_at=starts_at,
                ends_at=ends_at,
            )
            slots_ids_to_reserve = get_slots_ids_to_reserve(times_dict, starts_at)
            await insert_appointment(session, appointment)
            await insert_reservations(session, slots_ids_to_reserve, appointment.appointment_id)
            messages_to_answer = [
                MessageToAnswer(
                    messages.APPOINTMENT_SAVED.format(
                        appointment_view=form_appointment_view(appointment, with_date=True, for_admin=False),
                    ),
                    appointments_keyboard,
                ),
            ]
            messages_to_send = [
                MessageToSend(
                    user_id=ADMIN_TG_ID,
                    text=messages.NEW_APPOINTMENT_CREATED.format(
                        appointment_view=form_appointment_view(appointment, with_date=True, for_admin=True),
                    ),
                ),
            ]
            state_to_set = MakeAppointment.choose_action
            return _get_logic_result(
                messages_to_answer,
                state_to_set,
                data_to_set={},
                messages_to_send=messages_to_send,
            )
