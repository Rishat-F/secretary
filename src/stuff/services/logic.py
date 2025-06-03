from aiogram.fsm.state import State
from sqlalchemy.ext.asyncio import AsyncSession

from src import messages
from src.database import delete_service, get_services, insert_service, update_service
from src.models import Service
from src.stuff.common.keyboards import BACK, MAIN_MENU, back_main_keyboard
from src.stuff.common.logic import (
    LogicResult,
    MessageToAnswer,
    get_logic_result,
    show_services,
    to_main_menu_result,
)
from src.stuff.common.utils import (
    form_service_view,
    preprocess_text,
    validate_service_duration,
    validate_service_name,
    validate_service_price,
)
from src.stuff.services.exceptions import ServiceNameTooLongError
from src.stuff.services.keyboards import (
    CREATE,
    DELETE,
    DURATION,
    NAME,
    PRICE,
    SHOW_ALL_USLUGI,
    UPDATE,
    UPDATE_ANOTHER_USLUGA,
    get_services_to_update_keyboard,
    service_fields_keyboard,
    services_keyboard,
    set_service_new_field_keyboard,
)
from src.stuff.services.states import ServicesActions


async def choose_services_action_logic(user_input: str, session: AsyncSession) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        return to_main_menu_result()
    elif upper_text == SHOW_ALL_USLUGI.upper():
        services = await get_services(session)
        message_to_send = show_services(services, services_keyboard, show_duration=True)
        messages_to_answer = [message_to_send]
        return get_logic_result(messages_to_answer)
    elif upper_text == CREATE.upper():
        messages_to_answer = [ MessageToAnswer(messages.SET_SERVICE_NAME, back_main_keyboard) ]
        state_to_set = ServicesActions.set_name
        return get_logic_result(messages_to_answer, state_to_set)
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
            return get_logic_result(messages_to_answer, state_to_set, data_to_set)
        else:
            messages_to_answer = [ MessageToAnswer(messages.NO_SERVICES, services_keyboard) ]
            return get_logic_result(messages_to_answer)
    elif upper_text == DELETE.upper():
        services = await get_services(session)
        if services:
            services_to_delete = {str(pos): service.name for pos, service in enumerate(services, start=1)}
            data_to_set = services_to_delete
            state_to_set = ServicesActions.choose_service_to_delete
            message_to_send_1 = show_services(services, back_main_keyboard, show_duration=True)
            message_to_send_2 = MessageToAnswer(messages.CHOOSE_SERVICE_TO_DELETE, back_main_keyboard)
            messages_to_answer = [message_to_send_1, message_to_send_2]
            return get_logic_result(messages_to_answer, state_to_set, data_to_set)
        else:
            messages_to_answer = [ MessageToAnswer(messages.NO_SERVICES, services_keyboard) ]
            return get_logic_result(messages_to_answer)
    else:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_GIVEN_ACTION, services_keyboard) ]
        return get_logic_result(messages_to_answer)


async def set_service_name_logic(user_input: str, session: AsyncSession) -> LogicResult:
    text = preprocess_text(user_input)
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, services_keyboard) ]
        state_to_set = ServicesActions.choose_action
        return get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return to_main_menu_result()
    else:
        try:
            service_name = validate_service_name(text)
        except ServiceNameTooLongError as err:
            messages_to_answer = [ MessageToAnswer(str(err), back_main_keyboard) ]
            return get_logic_result(messages_to_answer)
        else:
            services = await get_services(session, filter_by={"name": service_name})
            if services:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.SERVICE_ALREADY_EXISTS.format(name=service_name),
                        back_main_keyboard,
                    ),
                ]
                return get_logic_result(messages_to_answer)
            else:
                messages_to_answer = [ MessageToAnswer(messages.SET_SERVICE_PRICE, back_main_keyboard) ]
                state_to_set = ServicesActions.set_price
                data_to_set = {"name": service_name}
                return get_logic_result(messages_to_answer, state_to_set, data_to_set)


async def set_service_price_logic(user_input: str) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.SET_SERVICE_NAME, back_main_keyboard) ]
        state_to_set = ServicesActions.set_name
        return get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return to_main_menu_result()
    else:
        possible_price = validate_service_price(text)
        if isinstance(possible_price, int):
            messages_to_answer = [ MessageToAnswer(messages.SET_SERVICE_DURATION, back_main_keyboard) ]
            state_to_set = ServicesActions.set_duration
            data_to_update = {"price": possible_price}
            return get_logic_result(messages_to_answer, state_to_set, data_to_update=data_to_update)
        else:
            error_message = possible_price
            messages_to_answer = [ MessageToAnswer(error_message, back_main_keyboard) ]
            return get_logic_result(messages_to_answer)


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
        return get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return to_main_menu_result()
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
            return get_logic_result(messages_to_answer, state_to_set, data_to_set={})
        else:
            error_message = possible_duration
            messages_to_answer = [ MessageToAnswer(error_message, back_main_keyboard) ]
            return get_logic_result(messages_to_answer)


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
        return get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return to_main_menu_result()
    else:
        pos_to_delete = text
        service_name_to_delete = services_to_delete.get(pos_to_delete)
        if service_name_to_delete is None:
            messages_to_answer = [ MessageToAnswer(messages.CHOOSE_SERVICE_TO_DELETE, back_main_keyboard) ]
            return get_logic_result(messages_to_answer)
        else:
            await delete_service(session, service_name_to_delete)
            messages_to_answer = [
                MessageToAnswer(
                    messages.SERVICE_DELETED.format(name=service_name_to_delete),
                    services_keyboard,
                ),
            ]
            state_to_set = ServicesActions.choose_action
            return get_logic_result(messages_to_answer, state_to_set, data_to_set={})


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
        return get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return to_main_menu_result()
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
        return get_logic_result(messages_to_answer, state_to_set, data_to_update=data_to_update)
    else:
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_GIVEN_SERVICES,
                get_services_to_update_keyboard(services_names),
            )
        ]
        return get_logic_result(messages_to_answer)


def _field_chosen_to_update(message_text: str, state_to_set: State) -> LogicResult:
    messages_to_answer = [ MessageToAnswer(message_text, set_service_new_field_keyboard) ]
    return get_logic_result(messages_to_answer, state_to_set)


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
        return get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return to_main_menu_result()
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
        return get_logic_result(messages_to_answer)


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
    return get_logic_result(messages_to_answer, state_to_set)


def _update_another_service(services_names: list[str]) -> LogicResult:
    state_to_set = ServicesActions.choose_service_to_update
    messages_to_answer = [
        MessageToAnswer(
            messages.CHOOSE_SERVICE_TO_UPDATE,
            get_services_to_update_keyboard(services_names),
        ),
    ]
    return get_logic_result(messages_to_answer, state_to_set)


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
        return to_main_menu_result()
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
            return get_logic_result(messages_to_answer)
        else:
            try:
                new_name = validate_service_name(text)
            except ServiceNameTooLongError as err:
                messages_to_answer = [ MessageToAnswer(str(err), set_service_new_field_keyboard) ]
                return get_logic_result(messages_to_answer)
            else:
                if new_name in services_names:
                    messages_to_answer = [
                        MessageToAnswer(
                            messages.SERVICE_ALREADY_EXISTS.format(name=new_name),
                            set_service_new_field_keyboard,
                        ),
                    ]
                    return get_logic_result(messages_to_answer)
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
                    return get_logic_result(messages_to_answer, data_to_update=data_to_update)


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
        return to_main_menu_result()
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
                return get_logic_result(messages_to_answer)
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
                return get_logic_result(messages_to_answer, data_to_update=data_to_update)
        else:
            error_message = possible_price
            messages_to_answer = [ MessageToAnswer(error_message, set_service_new_field_keyboard) ]
            return get_logic_result(messages_to_answer)


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
        return to_main_menu_result()
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
                return get_logic_result(messages_to_answer)
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
                return get_logic_result(messages_to_answer, data_to_update=data_to_update)
        else:
            error_message = possible_duration
            messages_to_answer = [ MessageToAnswer(error_message, set_service_new_field_keyboard) ]
            return get_logic_result(messages_to_answer)
