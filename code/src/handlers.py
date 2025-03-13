"""Обработчики бота."""

from datetime import datetime, time, timedelta

from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from exceptions import UslugaNameTooLongError
import messages
from config import ADMIN_TG_ID
from database import (
    delete_usluga,
    get_uslugi,
    get_active_zapisi,
    insert_usluga,
    insert_zapis,
    update_usluga,
)
from keyboards import (
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
    admin_main_keyboard,
    back_keyboard,
    back_main_keyboard,
    client_main_keyboard,
    get_days_keyboard,
    get_months_keyboard,
    get_times_keyboard,
    get_uslugi_to_update_keyboard,
    get_years_keyboard,
    set_usluga_new_field_keyboard,
    usluga_fields_keyboard,
    uslugi_keyboard,
    zapisi_keyboard,
)
from models import Usluga, Zapis
from states import UslugiActions, ZapisNaPriem
from utils import (
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


async def start_bot(message: types.Message):
    if message.from_user.id == ADMIN_TG_ID:
        main_keyboard = admin_main_keyboard
    else:
        main_keyboard = client_main_keyboard
    await message.answer(messages.GREETING, reply_markup=main_keyboard)


async def show_id(message: types.Message):
    if message.from_user.id == ADMIN_TG_ID:
        main_keyboard = admin_main_keyboard
    else:
        main_keyboard = client_main_keyboard
    await message.answer(
        messages.YOUR_ID.format(id=message.from_user.id), reply_markup=main_keyboard
    )


async def _show_uslugi(
    uslugi: list[Usluga],
    message: types.Message,
    keyboard: types.ReplyKeyboardMarkup,
    show_duration: bool,
) -> list[Usluga]:
    text = form_uslugi_list_text(uslugi, show_duration)
    await message.answer(text, reply_markup=keyboard)
    return uslugi


async def uslugi(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
):
    if message.from_user.id == ADMIN_TG_ID:
        await message.answer(messages.CHOOSE_ACTION, reply_markup=uslugi_keyboard)
        await state.set_state(UslugiActions.choose_action)
    else:
        uslugi = await get_uslugi(async_session)
        await _show_uslugi(uslugi, message, client_main_keyboard, show_duration=False)


async def choose_uslugi_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    upper_text = message.text.upper()
    if upper_text == BACK.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    elif upper_text == SHOW_ALL_USLUGI.upper():
        uslugi = await get_uslugi(async_session)
        await _show_uslugi(uslugi, message, uslugi_keyboard, show_duration=True)
    elif upper_text == CREATE.upper():
        await state.set_state(UslugiActions.set_name)
        await message.answer(messages.SET_USLUGA_NAME, reply_markup=back_main_keyboard)
    elif upper_text == UPDATE.upper():
        uslugi = await get_uslugi(async_session)
        if uslugi:
            uslugi_names = [usluga.name for usluga in uslugi]
            await state.set_data({"uslugi_names": uslugi_names})
            await state.set_state(UslugiActions.choose_usluga_to_update)
            await message.answer(
                messages.CHOOSE_USLUGA_TO_UPDATE,
                reply_markup=get_uslugi_to_update_keyboard(uslugi_names),
            )
        else:
            await message.answer(messages.NO_USLUGI, reply_markup=uslugi_keyboard)
    elif upper_text == DELETE.upper():
        uslugi = await get_uslugi(async_session)
        if uslugi:
            uslugi_to_delete = {str(pos): usluga.name for pos, usluga in enumerate(uslugi, start=1)}
            await state.set_data(uslugi_to_delete)
            await state.set_state(UslugiActions.choose_usluga_to_delete)
            await _show_uslugi(uslugi, message, back_main_keyboard, show_duration=True)
            await message.answer(messages.CHOOSE_USLUGA_TO_DELETE, reply_markup=back_main_keyboard)
        else:
            await message.answer(messages.NO_USLUGI, reply_markup=uslugi_keyboard)
    else:
        await message.answer(messages.CHOOSE_GIVEN_ACTION, reply_markup=uslugi_keyboard)


async def set_usluga_name(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    text = preprocess_text(message.text)
    upper_text = text.upper()
    if upper_text == BACK.upper():
        await state.set_state(UslugiActions.choose_action)
        await message.answer(messages.CHOOSE_ACTION, reply_markup=uslugi_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.set_data(data={})
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    else:
        try:
            usluga_name = validate_usluga_name(text)
        except UslugaNameTooLongError as err:
            await message.answer(str(err), reply_markup=back_main_keyboard)
        else:
            uslugi = await get_uslugi(async_session, filter_by={"name": usluga_name})
            if uslugi:
                await message.answer(
                    messages.USLUGA_ALREADY_EXISTS.format(name=usluga_name),
                    reply_markup=back_main_keyboard,
                )
            else:
                await state.set_data({"name": usluga_name})
                await state.set_state(UslugiActions.set_price)
                await message.answer(messages.SET_USLUGA_PRICE, reply_markup=back_main_keyboard)


async def set_usluga_price(message: types.Message, state: FSMContext) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        await state.set_state(UslugiActions.set_name)
        await message.answer(messages.SET_USLUGA_NAME, reply_markup=back_main_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    else:
        possible_price = validate_usluga_price(text)
        if isinstance(possible_price, int):
            await state.update_data({"price": possible_price})
            await state.set_state(UslugiActions.set_duration)
            await message.answer(messages.SET_USLUGA_DURATION, reply_markup=back_main_keyboard)
        else:
            error_message = possible_price
            await message.answer(error_message, reply_markup=back_main_keyboard)


async def set_usluga_duration(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        await state.set_state(UslugiActions.set_price)
        await message.answer(messages.SET_USLUGA_PRICE, reply_markup=back_main_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    else:
        possible_duration = validate_usluga_duration(text)
        if isinstance(possible_duration, int):
            data = await state.update_data({"duration": possible_duration})
            new_usluga = Usluga(**data)
            await insert_usluga(async_session, new_usluga)
            await message.answer(
                messages.USLUGA_CREATED.format(name=new_usluga.name),
                reply_markup=uslugi_keyboard,
            )
            await state.set_state(UslugiActions.choose_action)
            await state.set_data({})
        else:
            error_message = possible_duration
            await message.answer(error_message, reply_markup=back_main_keyboard)


async def choose_usluga_to_delete(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        await state.set_state(UslugiActions.choose_action)
        await message.answer(messages.CHOOSE_ACTION, reply_markup=uslugi_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    else:
        uslugi_to_delete = await state.get_data()
        pos_to_delete = text
        usluga_name_to_delete = uslugi_to_delete.get(pos_to_delete)
        if usluga_name_to_delete is None:
            await message.answer(
                messages.CHOOSE_USLUGA_TO_DELETE,
                reply_markup=back_main_keyboard,
            )
        else:
            await delete_usluga(async_session, usluga_name_to_delete)
            await state.set_state(UslugiActions.choose_action)
            await state.set_data({})
            await message.answer(
                messages.USLUGA_DELETED.format(name=usluga_name_to_delete),
                reply_markup=uslugi_keyboard,
            )


async def choose_usluga_to_update(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    data = await state.get_data()
    uslugi_names = data["uslugi_names"]
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        await state.set_state(UslugiActions.choose_action)
        await message.answer(messages.CHOOSE_ACTION, reply_markup=uslugi_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    elif text in uslugi_names:
        [chosen_usluga] = await get_uslugi(async_session, filter_by={"name": text})
        await state.set_state(UslugiActions.choose_usluga_field_to_update)
        await state.update_data(
            {
                "chosen_usluga_name": chosen_usluga.name,
                "chosen_usluga_price": chosen_usluga.price,
                "chosen_usluga_duration": chosen_usluga.duration,
            }
        )
        answer = (
            f"{form_usluga_view(chosen_usluga, show_duration=True)}\n"
            f"{messages.CHOOSE_FIELD_TO_CHANGE}"
        )
        await message.answer(
            answer,
            reply_markup=usluga_fields_keyboard,
        )
    else:
        await message.answer(
            messages.CHOOSE_GIVEN_USLUGI,
            reply_markup=get_uslugi_to_update_keyboard(uslugi_names),
        )


async def choose_usluga_field_to_update(
    message: types.Message,
    state: FSMContext,
) -> None:
    data = await state.get_data()
    uslugi_names = data["uslugi_names"]
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        await state.set_state(UslugiActions.choose_usluga_to_update)
        await message.answer(
            messages.CHOOSE_USLUGA_TO_UPDATE,
            reply_markup=get_uslugi_to_update_keyboard(uslugi_names),
        )
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    elif upper_text in NAME.upper():
        await state.set_state(UslugiActions.set_new_name)
        await message.answer(
            messages.SET_USLUGA_NEW_NAME,
            reply_markup=set_usluga_new_field_keyboard,
        )
    elif upper_text in PRICE.upper():
        await state.set_state(UslugiActions.set_new_price)
        await message.answer(
            messages.SET_USLUGA_NEW_PRICE,
            reply_markup=set_usluga_new_field_keyboard,
        )
    elif upper_text in DURATION.upper():
        await state.set_state(UslugiActions.set_new_duration)
        await message.answer(
            messages.SET_USLUGA_NEW_DURATION,
            reply_markup=set_usluga_new_field_keyboard,
        )
    else:
        await message.answer(
            messages.CHOOSE_GIVEN_FIELD_TO_CHANGE,
            reply_markup=usluga_fields_keyboard,
        )


async def set_usluga_new_name(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    data = await state.get_data()
    uslugi_names: list = data["uslugi_names"]
    old_name = data["chosen_usluga_name"]
    text = preprocess_text(message.text)
    upper_text = text.upper()
    if upper_text == BACK.upper():
        chosen_usluga = Usluga(
            name=old_name,
            price=data["chosen_usluga_price"],
            duration=data["chosen_usluga_duration"],
        )
        answer = (
            f"{form_usluga_view(chosen_usluga, show_duration=True)}\n"
            f"{messages.CHOOSE_FIELD_TO_CHANGE}"
        )
        await state.set_state(UslugiActions.choose_usluga_field_to_update)
        await message.answer(answer, reply_markup=usluga_fields_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    elif upper_text == UPDATE_ANOTHER_USLUGA.upper():
        await state.set_state(UslugiActions.choose_usluga_to_update)
        await message.answer(
            messages.CHOOSE_USLUGA_TO_UPDATE,
            reply_markup=get_uslugi_to_update_keyboard(uslugi_names),
        )
    else:
        if old_name == text:
            await message.answer(
                messages.USLUGA_OLD_NAME_AND_NEW_NAME_ARE_SIMILAR,
                reply_markup=set_usluga_new_field_keyboard,
            )
        else:
            try:
                new_name = validate_usluga_name(text)
            except UslugaNameTooLongError as err:
                await message.answer(str(err), reply_markup=set_usluga_new_field_keyboard)
            else:
                if new_name in uslugi_names:
                    await message.answer(
                        messages.USLUGA_ALREADY_EXISTS.format(name=new_name),
                        reply_markup=set_usluga_new_field_keyboard,
                    )
                else:
                    updated_uslugi_names = [
                        new_name if name == old_name else name
                        for name in uslugi_names
                    ]
                    await update_usluga(async_session, old_name, new_values={"name": new_name})
                    await state.update_data(
                        {"uslugi_names": updated_uslugi_names, "chosen_usluga_name": new_name}
                    )
                    await message.answer(
                        messages.USLUGA_NEW_NAME_SETTLED.format(
                            old_name=old_name,
                            new_name=new_name,
                        ),
                        reply_markup=set_usluga_new_field_keyboard,
                    )


async def set_usluga_new_price(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    data = await state.get_data()
    uslugi_names: list = data["uslugi_names"]
    usluga_name = data["chosen_usluga_name"]
    old_price = data["chosen_usluga_price"]
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        chosen_usluga = Usluga(
            name=usluga_name,
            price=old_price,
            duration=data["chosen_usluga_duration"],
        )
        answer = (
            f"{form_usluga_view(chosen_usluga, show_duration=True)}\n"
            f"{messages.CHOOSE_FIELD_TO_CHANGE}"
        )
        await state.set_state(UslugiActions.choose_usluga_field_to_update)
        await message.answer(answer, reply_markup=usluga_fields_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    elif upper_text == UPDATE_ANOTHER_USLUGA.upper():
        await state.set_state(UslugiActions.choose_usluga_to_update)
        await message.answer(
            messages.CHOOSE_USLUGA_TO_UPDATE,
            reply_markup=get_uslugi_to_update_keyboard(uslugi_names),
        )
    else:
        possible_price = validate_usluga_price(text)
        if isinstance(possible_price, int):
            new_price = possible_price
            if new_price == old_price:
                await message.answer(
                    messages.USLUGA_OLD_PRICE_AND_NEW_PRICE_ARE_SIMILAR,
                    reply_markup=set_usluga_new_field_keyboard,
                )
            else:
                await state.update_data({"chosen_usluga_price": new_price})
                await update_usluga(
                    async_session,
                    usluga_name,
                    new_values={"price": new_price},
                )
                await message.answer(
                    messages.USLUGA_NEW_PRICE_SETTLED.format(
                        usluga_name=usluga_name,
                        old_price=old_price,
                        new_price=new_price,
                    ),
                    reply_markup=set_usluga_new_field_keyboard,
                )
        else:
            error_message = possible_price
            await message.answer(error_message, reply_markup=set_usluga_new_field_keyboard)


async def set_usluga_new_duration(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    data = await state.get_data()
    uslugi_names: list = data["uslugi_names"]
    usluga_name = data["chosen_usluga_name"]
    old_duration = data["chosen_usluga_duration"]
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        chosen_usluga = Usluga(
            name=usluga_name,
            price=data["chosen_usluga_price"],
            duration=old_duration,
        )
        answer = (
            f"{form_usluga_view(chosen_usluga, show_duration=True)}\n"
            f"{messages.CHOOSE_FIELD_TO_CHANGE}"
        )
        await state.set_state(UslugiActions.choose_usluga_field_to_update)
        await message.answer(answer, reply_markup=usluga_fields_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=admin_main_keyboard)
    elif upper_text == UPDATE_ANOTHER_USLUGA.upper():
        await state.set_state(UslugiActions.choose_usluga_to_update)
        await message.answer(
            messages.CHOOSE_USLUGA_TO_UPDATE,
            reply_markup=get_uslugi_to_update_keyboard(uslugi_names),
        )
    else:
        possible_duration = validate_usluga_duration(text)
        if isinstance(possible_duration, int):
            new_duration = possible_duration
            if new_duration == old_duration:
                await message.answer(
                    messages.USLUGA_OLD_DURATION_AND_NEW_DURATION_ARE_SIMILAR,
                    reply_markup=set_usluga_new_field_keyboard,
                )
            else:
                await state.update_data({"chosen_usluga_duration": new_duration})
                await update_usluga(
                    async_session,
                    usluga_name,
                    new_values={"duration": new_duration},
                )
                await message.answer(
                    messages.USLUGA_NEW_DURATION_SETTLED.format(
                        usluga_name=usluga_name,
                        old_duration=old_duration,
                        new_duration=new_duration,
                    ),
                    reply_markup=set_usluga_new_field_keyboard,
                )
        else:
            error_message = possible_duration
            await message.answer(error_message, reply_markup=set_usluga_new_field_keyboard)


async def zapisi(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.from_user.id == ADMIN_TG_ID:
        zapisi = await get_active_zapisi(async_session)
        text = form_zapisi_list_text(zapisi, for_admin=True)
        await message.answer(text, reply_markup=admin_main_keyboard)
    else:
        await state.set_state(ZapisNaPriem.choose_action)
        await message.answer(messages.CHOOSE_ACTION, reply_markup=zapisi_keyboard)


async def choose_zapisi_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    upper_text = message.text.upper()
    if upper_text == BACK.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=client_main_keyboard)
    elif upper_text == ZAPIS_NA_PRIEM.upper():
        uslugi = await get_uslugi(async_session)
        if not uslugi:
            await message.answer(messages.NO_USLUGI, keyboard=zapisi_keyboard)
        else:
            uslugi_na_zapis = {str(pos): usluga.name for pos, usluga in enumerate(uslugi, start=1)}
            await state.set_data({"uslugi_na_zapis": uslugi_na_zapis})
            await state.set_state(ZapisNaPriem.choose_usluga)
            await _show_uslugi(uslugi, message, back_main_keyboard, show_duration=False)
            await message.answer(messages.CHOOSE_USLUGA_TO_ZAPIS, reply_markup=back_main_keyboard)
    elif upper_text == SHOW_ACTIVE_ZAPISI.upper():
        zapisi = await get_active_zapisi(
            async_session,
            filter_by={"client_id": message.from_user.id},
        )
        text = form_zapisi_list_text(zapisi, for_admin=False)
        await message.answer(text, reply_markup=zapisi_keyboard)
    else:
        await message.answer(messages.CHOOSE_GIVEN_ACTION, reply_markup=zapisi_keyboard)


async def choose_usluga_to_zapis(message: types.Message, state: FSMContext) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        await state.set_state(ZapisNaPriem.choose_action)
        await message.answer(messages.MAIN_MENU, reply_markup=zapisi_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=client_main_keyboard)
    else:
        data = await state.get_data()
        uslugi_to_zapis = data["uslugi_na_zapis"]
        pos_to_zapis = text
        usluga_name_to_zapis = uslugi_to_zapis.get(pos_to_zapis)
        if usluga_name_to_zapis is None:
            await message.answer(
                messages.CHOOSE_USLUGA_TO_ZAPIS,
                reply_markup=back_keyboard,
            )
        else:
            current_year = datetime.today().year
            years_to_choose = [current_year, (current_year + 1)]
            await state.set_state(ZapisNaPriem.choose_year)
            await state.set_data(
                {
                    "chosen_usluga_name": usluga_name_to_zapis,
                    "years_to_choose": years_to_choose,
                }
            )
            await message.answer(
                messages.CHOOSE_YEAR,
                reply_markup=get_years_keyboard(years_to_choose),
            )


async def choose_year_to_zapis(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        uslugi = await get_uslugi(async_session)
        if not uslugi:
            await state.clear()
            await message.answer(messages.NO_USLUGI, keyboard=client_main_keyboard)
        else:
            uslugi_na_zapis = {str(pos): usluga.name for pos, usluga in enumerate(uslugi, start=1)}
            await state.set_data({"uslugi_na_zapis": uslugi_na_zapis})
            await state.set_state(ZapisNaPriem.choose_usluga)
            await _show_uslugi(uslugi, message, back_keyboard, show_duration=False)
            await message.answer(messages.CHOOSE_USLUGA_TO_ZAPIS, reply_markup=back_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=client_main_keyboard)
    else:
        data = await state.get_data()
        years_to_choose = data["years_to_choose"]
        if text not in [str(year) for year in years_to_choose]:
            await message.answer(
                messages.CHOOSE_GIVEN_YEAR,
                reply_markup=get_years_keyboard(years_to_choose),
            )
        else:
            chosen_year = int(text)
            months_to_choose = get_months(chosen_year)
            await state.set_state(ZapisNaPriem.choose_month)
            await state.update_data(
                {
                    "chosen_year": chosen_year,
                    "months_to_choose": months_to_choose,
                }
            )
            await message.answer(
                messages.CHOOSE_MONTH,
                reply_markup=get_months_keyboard(months_to_choose),
            )


async def choose_month_to_zapis(message: types.Message, state: FSMContext) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        current_year = datetime.today().year
        years_to_choose = [current_year, (current_year + 1)]
        await state.set_state(ZapisNaPriem.choose_year)
        await state.update_data({"years_to_choose": years_to_choose})
        await message.answer(
            messages.CHOOSE_YEAR,
            reply_markup=get_years_keyboard(years_to_choose),
        )
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=client_main_keyboard)
    else:
        data = await state.get_data()
        months_to_choose = data["months_to_choose"]
        if text not in months_to_choose:
            await message.answer(
                messages.CHOOSE_GIVEN_MONTH,
                reply_markup=get_months_keyboard(months_to_choose),
            )
        else:
            chosen_year = data["chosen_year"]
            chosen_month = text
            days_to_choose = get_days(chosen_year, chosen_month)
            await state.set_state(ZapisNaPriem.choose_day)
            await state.update_data(
                {
                    "chosen_month": chosen_month,
                    "days_to_choose": days_to_choose,
                }
            )
            await message.answer(
                messages.CHOOSE_DAY,
                reply_markup=get_days_keyboard(days_to_choose),
            )


async def choose_day_to_zapis(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        current_year = datetime.today().year
        months_to_choose = get_months(current_year)
        await state.set_state(ZapisNaPriem.choose_month)
        await state.update_data({"months_to_choose": months_to_choose})
        await message.answer(
            messages.CHOOSE_MONTH,
            reply_markup=get_months_keyboard(months_to_choose),
        )
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=client_main_keyboard)
    else:
        data = await state.get_data()
        days_to_choose = data["days_to_choose"]
        if text not in [str(day) for day in days_to_choose]:
            await message.answer(
                messages.CHOOSE_GIVEN_DAY,
                reply_markup=get_days_keyboard(days_to_choose),
            )
        else:
            chosen_usluga_name = data["chosen_usluga_name"]
            chosen_year = data["chosen_year"]
            chosen_month = data["chosen_month"]
            chosen_day = int(text)
            times_to_choose = get_available_times(
                async_session,
                chosen_usluga_name,
                chosen_year,
                chosen_month, chosen_day,
            )
            await state.set_state(ZapisNaPriem.choose_time)
            await state.update_data(
                {
                    "chosen_day": chosen_day,
                    "times_to_choose": times_to_choose,
                }
            )
            await message.answer(
                messages.CHOOSE_TIME,
                reply_markup=get_times_keyboard(times_to_choose),
            )


async def choose_time_to_zapis(
    message: types.Message,
    bot: Bot,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    data = await state.get_data()
    if upper_text == BACK.upper():
        chosen_year = data["chosen_year"]
        chosen_month = data["chosen_month"]
        days_to_choose = get_days(chosen_year, chosen_month)
        await state.set_state(ZapisNaPriem.choose_day)
        await state.update_data({"days_to_choose": days_to_choose})
        await message.answer(
            messages.CHOOSE_DAY,
            reply_markup=get_days_keyboard(days_to_choose),
        )
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=client_main_keyboard)
    else:
        times_to_choose = data["times_to_choose"]
        if text not in times_to_choose:
            await message.answer(
                messages.CHOOSE_GIVEN_TIME,
                reply_markup=get_times_keyboard(times_to_choose),
            )
        else:
            chosen_usluga_name = data["chosen_usluga_name"]
            [chosen_usluga] = await get_uslugi(async_session, filter_by={"name": chosen_usluga_name})
            chosen_year = data["chosen_year"]
            chosen_month = months_swapped[data["chosen_month"]]
            chosen_day = data["chosen_day"]
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
                client_id=message.from_user.id,
                usluga_id=chosen_usluga.usluga_id,
                starts_at=starts_at,
                ends_at=ends_at,
            )
            await insert_zapis(async_session, zapis)
            await state.set_state(ZapisNaPriem.choose_action)
            await state.set_data({})
            await message.answer(
                messages.ZAPIS_SAVED.format(
                    zapis_view=form_zapis_view(zapis, with_date=True, for_admin=False),
                ),
                reply_markup=zapisi_keyboard,
            )
            await bot.send_message(
                ADMIN_TG_ID,
                messages.NEW_ZAPIS_CREATED.format(
                    zapis_view=form_zapis_view(zapis, with_date=True, for_admin=True),
                ),
            )
