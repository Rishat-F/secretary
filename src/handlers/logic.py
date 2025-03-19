from dataclasses import dataclass
from datetime import datetime, time, timedelta

from aiogram import types
from aiogram.fsm.state import State
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src import messages
from src.database import (
    delete_usluga,
    get_uslugi,
    get_active_zapisi,
    insert_usluga,
    insert_zapis,
    update_usluga,
)
from src.exceptions import UslugaNameTooLongError
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
    get_uslugi_to_update_keyboard,
    get_years_keyboard,
    main_keyboard,
    set_usluga_new_field_keyboard,
    usluga_fields_keyboard,
    uslugi_keyboard,
    zapisi_keyboard,
)
from src.models import Usluga, Zapis
from src.secrets import ADMIN_TG_ID
from src.states import UslugiActions, ZapisNaPriem
from src.utils import (
    form_usluga_view,
    form_uslugi_list_text,
    form_zapis_view,
    form_zapisi_list_text,
    get_available_times,
    get_days,
    get_months,
    months_swapped,
    preprocess_text,
    validate_usluga_duration,
    validate_usluga_name,
    validate_usluga_price,
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


def _show_uslugi(
    uslugi: list[Usluga],
    keyboard: types.ReplyKeyboardMarkup,
    show_duration: bool,
) -> MessageToAnswer:
    text = form_uslugi_list_text(uslugi, show_duration)
    message_to_send = MessageToAnswer(text, keyboard)
    return message_to_send


async def uslugi_logic(
    user_id: int,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    if user_id == ADMIN_TG_ID:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, uslugi_keyboard) ]
        state_to_set = UslugiActions.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)
    else:
        uslugi = await get_uslugi(async_session)
        message_to_send = _show_uslugi(uslugi, main_keyboard, show_duration=False)
        messages_to_answer = [message_to_send]
        return _get_logic_result(messages_to_answer)


async def choose_uslugi_action_logic(
    user_input: str,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        return _to_main_menu_result()
    elif upper_text == SHOW_ALL_USLUGI.upper():
        uslugi = await get_uslugi(async_session)
        message_to_send = _show_uslugi(uslugi, uslugi_keyboard, show_duration=True)
        messages_to_answer = [message_to_send]
        return _get_logic_result(messages_to_answer)
    elif upper_text == CREATE.upper():
        messages_to_answer = [ MessageToAnswer(messages.SET_USLUGA_NAME, back_main_keyboard) ]
        state_to_set = UslugiActions.set_name
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == UPDATE.upper():
        uslugi = await get_uslugi(async_session)
        if uslugi:
            uslugi_names = [usluga.name for usluga in uslugi]
            data_to_set = {"uslugi_names": uslugi_names}
            state_to_set = UslugiActions.choose_usluga_to_update
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_USLUGA_TO_UPDATE,
                    get_uslugi_to_update_keyboard(uslugi_names),
                ),
            ]
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set)
        else:
            messages_to_answer = [ MessageToAnswer(messages.NO_USLUGI, uslugi_keyboard) ]
            return _get_logic_result(messages_to_answer)
    elif upper_text == DELETE.upper():
        uslugi = await get_uslugi(async_session)
        if uslugi:
            uslugi_to_delete = {str(pos): usluga.name for pos, usluga in enumerate(uslugi, start=1)}
            data_to_set = uslugi_to_delete
            state_to_set = UslugiActions.choose_usluga_to_delete
            message_to_send_1 = _show_uslugi(uslugi, back_main_keyboard, show_duration=True)
            message_to_send_2 = MessageToAnswer(messages.CHOOSE_USLUGA_TO_DELETE, back_main_keyboard)
            messages_to_answer = [message_to_send_1, message_to_send_2]
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set)
        else:
            messages_to_answer = [ MessageToAnswer(messages.NO_USLUGI, uslugi_keyboard) ]
            return _get_logic_result(messages_to_answer)
    else:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_GIVEN_ACTION, uslugi_keyboard) ]
        return _get_logic_result(messages_to_answer)


async def set_usluga_name_logic(
    user_input: str,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    text = preprocess_text(user_input)
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, uslugi_keyboard) ]
        state_to_set = UslugiActions.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        try:
            usluga_name = validate_usluga_name(text)
        except UslugaNameTooLongError as err:
            messages_to_answer = [ MessageToAnswer(str(err), back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)
        else:
            uslugi = await get_uslugi(async_session, filter_by={"name": usluga_name})
            if uslugi:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.USLUGA_ALREADY_EXISTS.format(name=usluga_name),
                        back_main_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer)
            else:
                messages_to_answer = [ MessageToAnswer(messages.SET_USLUGA_PRICE, back_main_keyboard) ]
                state_to_set = UslugiActions.set_price
                data_to_set = {"name": usluga_name}
                return _get_logic_result(messages_to_answer, state_to_set, data_to_set)


async def set_usluga_price_logic(user_input: str) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.SET_USLUGA_NAME, back_main_keyboard) ]
        state_to_set = UslugiActions.set_name
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        possible_price = validate_usluga_price(text)
        if isinstance(possible_price, int):
            messages_to_answer = [ MessageToAnswer(messages.SET_USLUGA_DURATION, back_main_keyboard) ]
            state_to_set = UslugiActions.set_duration
            data_to_update = {"price": possible_price}
            return _get_logic_result(messages_to_answer, state_to_set, data_to_update=data_to_update)
        else:
            error_message = possible_price
            messages_to_answer = [ MessageToAnswer(error_message, back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)


async def set_usluga_duration_logic(
    user_input: str,
    async_session: async_sessionmaker[AsyncSession],
    state_data: dict,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.SET_USLUGA_PRICE, back_main_keyboard) ]
        state_to_set = UslugiActions.set_price
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        possible_duration = validate_usluga_duration(text)
        if isinstance(possible_duration, int):
            state_data.update({"duration": possible_duration})
            new_usluga = Usluga(**state_data)
            await insert_usluga(async_session, new_usluga)
            messages_to_answer = [
                MessageToAnswer(
                    messages.USLUGA_CREATED.format(name=new_usluga.name),
                    uslugi_keyboard,
                ),
            ]
            state_to_set = UslugiActions.choose_action
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set={})
        else:
            error_message = possible_duration
            messages_to_answer = [ MessageToAnswer(error_message, back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)


async def choose_usluga_to_delete_logic(
    user_input: str,
    async_session: async_sessionmaker[AsyncSession],
    uslugi_to_delete: dict,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, uslugi_keyboard) ]
        state_to_set = UslugiActions.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        pos_to_delete = text
        usluga_name_to_delete = uslugi_to_delete.get(pos_to_delete)
        if usluga_name_to_delete is None:
            messages_to_answer = [ MessageToAnswer(messages.CHOOSE_USLUGA_TO_DELETE, back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)
        else:
            await delete_usluga(async_session, usluga_name_to_delete)
            messages_to_answer = [
                MessageToAnswer(
                    messages.USLUGA_DELETED.format(name=usluga_name_to_delete),
                    uslugi_keyboard,
                ),
            ]
            state_to_set = UslugiActions.choose_action
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set={})


async def choose_usluga_to_update_logic(
    user_input: str,
    async_session: async_sessionmaker[AsyncSession],
    uslugi_names: list[str],
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, uslugi_keyboard) ]
        state_to_set = UslugiActions.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif text in uslugi_names:
        [chosen_usluga] = await get_uslugi(async_session, filter_by={"name": text})
        answer = (
            f"{form_usluga_view(chosen_usluga, show_duration=True)}\n"
            f"{messages.CHOOSE_FIELD_TO_CHANGE}"
        )
        messages_to_answer = [ MessageToAnswer(answer, usluga_fields_keyboard) ]
        state_to_set = UslugiActions.choose_usluga_field_to_update
        data_to_update = {
            "chosen_usluga_name": chosen_usluga.name,
            "chosen_usluga_price": chosen_usluga.price,
            "chosen_usluga_duration": chosen_usluga.duration,
        }
        return _get_logic_result(messages_to_answer, state_to_set, data_to_update=data_to_update)
    else:
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_GIVEN_USLUGI,
                get_uslugi_to_update_keyboard(uslugi_names),
            )
        ]
        return _get_logic_result(messages_to_answer)


def _field_chosen_to_update(message_text: str, state_to_set: State) -> LogicResult:
    messages_to_answer = [ MessageToAnswer(message_text, set_usluga_new_field_keyboard) ]
    return _get_logic_result(messages_to_answer, state_to_set)


async def choose_usluga_field_to_update_logic(
    user_input: str,
    uslugi_names: list[str],
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_USLUGA_TO_UPDATE,
                get_uslugi_to_update_keyboard(uslugi_names),
            ),
        ]
        state_to_set = UslugiActions.choose_usluga_to_update
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif upper_text in NAME.upper():
        return _field_chosen_to_update(
            message_text=messages.SET_USLUGA_NEW_NAME,
            state_to_set=UslugiActions.set_new_name,
        )
    elif upper_text in PRICE.upper():
        return _field_chosen_to_update(
            message_text=messages.SET_USLUGA_NEW_PRICE,
            state_to_set=UslugiActions.set_new_price,
        )
    elif upper_text in DURATION.upper():
        return _field_chosen_to_update(
            message_text=messages.SET_USLUGA_NEW_DURATION,
            state_to_set=UslugiActions.set_new_duration,
        )
    else:
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_GIVEN_FIELD_TO_CHANGE,
                usluga_fields_keyboard,
            ),
        ]
        return _get_logic_result(messages_to_answer)


def _back_from_changing_usluga_field(state_data: dict) -> LogicResult:
    chosen_usluga = Usluga(
        name=state_data["chosen_usluga_name"],
        price=state_data["chosen_usluga_price"],
        duration=state_data["chosen_usluga_duration"],
    )
    answer = (
        f"{form_usluga_view(chosen_usluga, show_duration=True)}\n"
        f"{messages.CHOOSE_FIELD_TO_CHANGE}"
    )
    messages_to_answer = [ MessageToAnswer(answer, usluga_fields_keyboard) ]
    state_to_set = UslugiActions.choose_usluga_field_to_update
    return _get_logic_result(messages_to_answer, state_to_set)


def _update_another_usluga(uslugi_names: list[str]) -> LogicResult:
    state_to_set = UslugiActions.choose_usluga_to_update
    messages_to_answer = [
        MessageToAnswer(
            messages.CHOOSE_USLUGA_TO_UPDATE,
            get_uslugi_to_update_keyboard(uslugi_names),
        ),
    ]
    return _get_logic_result(messages_to_answer, state_to_set)


async def set_usluga_new_name_logic(
    user_input: str,
    async_session: async_sessionmaker[AsyncSession],
    state_data: dict,
) -> LogicResult:
    text = preprocess_text(user_input)
    upper_text = text.upper()
    uslugi_names: list = state_data["uslugi_names"]
    if upper_text == BACK.upper():
        return _back_from_changing_usluga_field(state_data)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif upper_text == UPDATE_ANOTHER_USLUGA.upper():
        return _update_another_usluga(uslugi_names)
    else:
        old_name = state_data["chosen_usluga_name"]
        if old_name == text:
            messages_to_answer = [
                MessageToAnswer(
                    messages.USLUGA_OLD_NAME_AND_NEW_NAME_ARE_SIMILAR,
                    set_usluga_new_field_keyboard,
                ),
            ]
            return _get_logic_result(messages_to_answer)
        else:
            try:
                new_name = validate_usluga_name(text)
            except UslugaNameTooLongError as err:
                messages_to_answer = [ MessageToAnswer(str(err), set_usluga_new_field_keyboard) ]
                return _get_logic_result(messages_to_answer)
            else:
                if new_name in uslugi_names:
                    messages_to_answer = [
                        MessageToAnswer(
                            messages.USLUGA_ALREADY_EXISTS.format(name=new_name),
                            set_usluga_new_field_keyboard,
                        ),
                    ]
                    return _get_logic_result(messages_to_answer)
                else:
                    updated_uslugi_names = [
                        new_name if name == old_name else name
                        for name in uslugi_names
                    ]
                    await update_usluga(async_session, old_name, new_values={"name": new_name})
                    data_to_update = {
                        "uslugi_names": updated_uslugi_names,
                        "chosen_usluga_name": new_name,
                    }
                    messages_to_answer = [
                        MessageToAnswer(
                            messages.USLUGA_NEW_NAME_SETTLED.format(
                                old_name=old_name,
                                new_name=new_name,
                            ),
                            set_usluga_new_field_keyboard,
                        ),
                    ]
                    return _get_logic_result(messages_to_answer, data_to_update=data_to_update)


async def set_usluga_new_price_logic(
    user_input: str,
    async_session: async_sessionmaker[AsyncSession],
    state_data: dict,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    uslugi_names: list = state_data["uslugi_names"]
    if upper_text == BACK.upper():
        return _back_from_changing_usluga_field(state_data)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif upper_text == UPDATE_ANOTHER_USLUGA.upper():
        return _update_another_usluga(uslugi_names)
    else:
        possible_price = validate_usluga_price(text)
        if isinstance(possible_price, int):
            new_price = possible_price
            old_price = state_data["chosen_usluga_price"]
            if new_price == old_price:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.USLUGA_OLD_PRICE_AND_NEW_PRICE_ARE_SIMILAR,
                        set_usluga_new_field_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer)
            else:
                usluga_name = state_data["chosen_usluga_name"]
                await update_usluga(
                    async_session,
                    usluga_name,
                    new_values={"price": new_price},
                )
                data_to_update = {"chosen_usluga_price": new_price}
                messages_to_answer = [
                    MessageToAnswer(
                        messages.USLUGA_NEW_PRICE_SETTLED.format(
                            usluga_name=usluga_name,
                            old_price=old_price,
                            new_price=new_price,
                        ),
                        set_usluga_new_field_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer, data_to_update=data_to_update)
        else:
            error_message = possible_price
            messages_to_answer = [ MessageToAnswer(error_message, set_usluga_new_field_keyboard) ]
            return _get_logic_result(messages_to_answer)


async def set_usluga_new_duration_logic(
    user_input: str,
    async_session: async_sessionmaker[AsyncSession],
    state_data: dict,
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    uslugi_names: list = state_data["uslugi_names"]
    if upper_text == BACK.upper():
        return _back_from_changing_usluga_field(state_data)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    elif upper_text == UPDATE_ANOTHER_USLUGA.upper():
        return _update_another_usluga(uslugi_names)
    else:
        possible_duration = validate_usluga_duration(text)
        if isinstance(possible_duration, int):
            new_duration = possible_duration
            old_duration = state_data["chosen_usluga_duration"]
            if new_duration == old_duration:
                messages_to_answer = [
                    MessageToAnswer(
                        messages.USLUGA_OLD_DURATION_AND_NEW_DURATION_ARE_SIMILAR,
                        set_usluga_new_field_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer)
            else:
                usluga_name = state_data["chosen_usluga_name"]
                await update_usluga(
                    async_session,
                    usluga_name,
                    new_values={"duration": new_duration},
                )
                data_to_update = {"chosen_usluga_duration": new_duration}
                messages_to_answer = [
                    MessageToAnswer(
                        messages.USLUGA_NEW_DURATION_SETTLED.format(
                            usluga_name=usluga_name,
                            old_duration=old_duration,
                            new_duration=new_duration,
                        ),
                        set_usluga_new_field_keyboard,
                    ),
                ]
                return _get_logic_result(messages_to_answer, data_to_update=data_to_update)
        else:
            error_message = possible_duration
            messages_to_answer = [ MessageToAnswer(error_message, set_usluga_new_field_keyboard) ]
            return _get_logic_result(messages_to_answer)


async def zapisi_logic(
    user_id: int,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    if user_id == ADMIN_TG_ID:
        zapisi = await get_active_zapisi(async_session)
        text = form_zapisi_list_text(zapisi, for_admin=True)
        messages_to_answer = [ MessageToAnswer(text, main_keyboard) ]
        return _get_logic_result(messages_to_answer)
    else:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, zapisi_keyboard) ]
        state_to_set = ZapisNaPriem.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)


async def choose_zapisi_action_logic(
    user_input: str,
    user_id: int,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        return _to_main_menu_result()
    elif upper_text == ZAPIS_NA_PRIEM.upper():
        uslugi = await get_uslugi(async_session)
        if not uslugi:
            messages_to_answer = [ MessageToAnswer(messages.NO_USLUGI, zapisi_keyboard) ]
            return _get_logic_result(messages_to_answer)
        else:
            uslugi_na_zapis = {str(pos): usluga.name for pos, usluga in enumerate(uslugi, start=1)}
            message_to_send_1 = _show_uslugi(uslugi, back_main_keyboard, show_duration=False)
            message_to_send_2 = MessageToAnswer(messages.CHOOSE_USLUGA_TO_ZAPIS, back_main_keyboard)
            messages_to_answer = [message_to_send_1, message_to_send_2]
            state_to_set = ZapisNaPriem.choose_usluga
            data_to_set = {"uslugi_na_zapis": uslugi_na_zapis}
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set)
    elif upper_text == SHOW_ACTIVE_ZAPISI.upper():
        zapisi = await get_active_zapisi(async_session, filter_by={"client_id": user_id})
        text = form_zapisi_list_text(zapisi, for_admin=False)
        messages_to_answer = [ MessageToAnswer(text, zapisi_keyboard) ]
        return _get_logic_result(messages_to_answer)
    else:
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_GIVEN_ACTION, zapisi_keyboard) ]
        return _get_logic_result(messages_to_answer)


async def choose_usluga_to_zapis_logic(user_input: str, state_data: dict) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        messages_to_answer = [ MessageToAnswer(messages.CHOOSE_ACTION, zapisi_keyboard) ]
        state_to_set = ZapisNaPriem.choose_action
        return _get_logic_result(messages_to_answer, state_to_set)
    elif upper_text == MAIN_MENU.upper():
        return _to_main_menu_result()
    else:
        uslugi_to_zapis = state_data["uslugi_na_zapis"]
        pos_to_zapis = text
        usluga_name_to_zapis = uslugi_to_zapis.get(pos_to_zapis)
        if usluga_name_to_zapis is None:
            messages_to_answer = [ MessageToAnswer(messages.CHOOSE_USLUGA_TO_ZAPIS, back_main_keyboard) ]
            return _get_logic_result(messages_to_answer)
        else:
            current_year = datetime.today().year
            years_to_choose = [current_year, (current_year + 1)]
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_YEAR,
                    get_years_keyboard(years_to_choose),
                ),
            ]
            state_to_set = ZapisNaPriem.choose_year
            data_to_set = {
                "chosen_usluga_name": usluga_name_to_zapis,
                "years_to_choose": years_to_choose,
            }
            return _get_logic_result(messages_to_answer, state_to_set, data_to_set)


async def choose_year_to_zapis_logic(
    user_input: str,
    state_data: dict,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        uslugi = await get_uslugi(async_session)
        if not uslugi:
            return _to_main_menu_result(messages.NO_USLUGI)
        else:
            uslugi_na_zapis = {str(pos): usluga.name for pos, usluga in enumerate(uslugi, start=1)}
            message_to_send_1 = _show_uslugi(uslugi, back_main_keyboard, show_duration=False)
            message_to_send_2 = MessageToAnswer( messages.CHOOSE_USLUGA_TO_ZAPIS, back_main_keyboard)
            messages_to_answer = [message_to_send_1, message_to_send_2]
            state_to_set = ZapisNaPriem.choose_usluga
            data_to_set = {"uslugi_na_zapis": uslugi_na_zapis}
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
            chosen_year = int(text)
            months_to_choose = get_months(chosen_year)
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_MONTH,
                    get_months_keyboard(months_to_choose),
                ),
            ]
            state_to_set = ZapisNaPriem.choose_month
            data_to_update = {
                "chosen_year": chosen_year,
                "months_to_choose": months_to_choose,
            }
            return _get_logic_result(
                messages_to_answer,
                state_to_set,
                data_to_update=data_to_update,
            )


async def choose_month_to_zapis_logic(user_input: str, state_data: dict) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        current_year = datetime.today().year
        years_to_choose = [current_year, (current_year + 1)]
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_YEAR,
                get_years_keyboard(years_to_choose),
            ),
        ]
        state_to_set = ZapisNaPriem.choose_year
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
            chosen_year = state_data["chosen_year"]
            chosen_month = text
            days_to_choose = get_days(chosen_year, chosen_month)
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_DAY,
                    get_days_keyboard(days_to_choose),
                ),
            ]
            state_to_set = ZapisNaPriem.choose_day
            data_to_update = {
                "chosen_month": chosen_month,
                "days_to_choose": days_to_choose,
            }
            return _get_logic_result(
                messages_to_answer,
                state_to_set,
                data_to_update=data_to_update,
            )


async def choose_day_to_zapis_logic(
    user_input: str,
    state_data: dict,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        current_year = datetime.today().year
        months_to_choose = get_months(current_year)
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_MONTH,
                get_months_keyboard(months_to_choose),
            ),
        ]
        state_to_set = ZapisNaPriem.choose_month
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
            chosen_usluga_name = state_data["chosen_usluga_name"]
            chosen_year = state_data["chosen_year"]
            chosen_month = state_data["chosen_month"]
            chosen_day = int(text)
            times_to_choose = get_available_times(
                async_session,
                chosen_usluga_name,
                chosen_year,
                chosen_month, chosen_day,
            )
            messages_to_answer = [
                MessageToAnswer(
                    messages.CHOOSE_TIME,
                    get_times_keyboard(times_to_choose),
                ),
            ]
            state_to_set = ZapisNaPriem.choose_time
            data_to_update = {
                "chosen_day": chosen_day,
                "times_to_choose": times_to_choose,
            }
            return _get_logic_result(
                messages_to_answer,
                state_to_set,
                data_to_update=data_to_update,
            )


async def choose_time_to_zapis_logic(
    user_input: str,
    user_id: int,
    state_data: dict,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    text = user_input.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        chosen_year = state_data["chosen_year"]
        chosen_month = state_data["chosen_month"]
        days_to_choose = get_days(chosen_year, chosen_month)
        messages_to_answer = [
            MessageToAnswer(
                messages.CHOOSE_DAY,
                get_days_keyboard(days_to_choose),
            ),
        ]
        state_to_set = ZapisNaPriem.choose_day
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
            chosen_usluga_name = state_data["chosen_usluga_name"]
            [chosen_usluga] = await get_uslugi(async_session, filter_by={"name": chosen_usluga_name})
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
            ends_at = starts_at + timedelta(minutes=chosen_usluga.duration)
            zapis = Zapis(
                client_id=user_id,
                usluga_id=chosen_usluga.usluga_id,
                starts_at=starts_at,
                ends_at=ends_at,
            )
            await insert_zapis(async_session, zapis)
            messages_to_answer = [
                MessageToAnswer(
                    messages.ZAPIS_SAVED.format(
                        zapis_view=form_zapis_view(zapis, with_date=True, for_admin=False),
                    ),
                    zapisi_keyboard,
                ),
            ]
            messages_to_send = [
                MessageToSend(
                    user_id=ADMIN_TG_ID,
                    text=messages.NEW_ZAPIS_CREATED.format(
                        zapis_view=form_zapis_view(zapis, with_date=True, for_admin=True),
                    ),
                ),
            ]
            state_to_set = ZapisNaPriem.choose_action
            return _get_logic_result(
                messages_to_answer,
                state_to_set,
                data_to_set={},
                messages_to_send=messages_to_send,
            )
