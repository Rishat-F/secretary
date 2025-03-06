"""Обработчики бота."""

from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from exceptions import UslugaNameTooLongError
import messages
from config import ADMIN_TG_ID
from database import delete_usluga, get_uslugi, insert_usluga
from keyboards import (
    BACK,
    CREATE,
    DELETE,
    MAIN_MENU,
    SHOW_ALL_USLUGI,
    back_keyboard,
    main_keyboard,
    uslugi_keyboard,
)
from models import Usluga
from states import UslugiActions
from utils import (
    form_uslugi_list_text,
    preprocess_text,
    validate_usluga_duration,
    validate_usluga_name,
    validate_usluga_price,
)


async def start_bot(message: types.Message):
    await message.answer(messages.GREETING, reply_markup=main_keyboard)


async def show_id(message: types.Message):
    await message.answer(
        messages.YOUR_ID.format(id=message.from_user.id), reply_markup=main_keyboard
    )


async def _show_uslugi(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    keyboard: types.ReplyKeyboardMarkup,
    show_duration: bool,
) -> list[Usluga]:
    uslugi = await get_uslugi(async_session)
    text = form_uslugi_list_text(uslugi, show_duration)
    await message.answer(text, reply_markup=keyboard)
    return uslugi


async def uslugi(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
):
    if message.from_user.id != ADMIN_TG_ID:
        await _show_uslugi(message, async_session, main_keyboard, show_duration=False)
    else:
        await message.answer(messages.CHOOSE_ACTION, reply_markup=uslugi_keyboard)
        await state.set_state(UslugiActions.choose_action)


async def choose_uslugi_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    upper_text = message.text.upper()
    if upper_text == BACK.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=main_keyboard)
    elif upper_text == SHOW_ALL_USLUGI.upper():
        await _show_uslugi(message, async_session, uslugi_keyboard, show_duration=True)
    elif upper_text == CREATE.upper():
        await state.set_state(UslugiActions.set_name)
        await message.answer(messages.SET_USLUGA_NAME, reply_markup=back_keyboard)
    elif upper_text == DELETE.upper():
        await state.set_state(UslugiActions.choose_usluga_to_delete)
        uslugi = await _show_uslugi(message, async_session, back_keyboard, show_duration=True)
        uslugi_to_delete = {str(pos): usluga.name for pos, usluga in enumerate(uslugi, start=1)}
        await state.set_data(uslugi_to_delete)
        await message.answer(messages.CHOOSE_USLUGA_TO_DELETE, reply_markup=back_keyboard)
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
        await message.answer(messages.MAIN_MENU, reply_markup=main_keyboard)
    else:
        try:
            usluga_name = validate_usluga_name(text)
        except UslugaNameTooLongError as err:
            await message.answer(str(err), reply_markup=back_keyboard)
        else:
            uslugi = await get_uslugi(async_session, filter_by={"name": usluga_name})
            if uslugi:
                await message.answer(
                    messages.USLUGA_ALREADY_EXISTS.format(name=usluga_name),
                    reply_markup=back_keyboard,
                )
            else:
                await state.set_data({"name": usluga_name})
                await state.set_state(UslugiActions.set_price)
                await message.answer(messages.SET_USLUGA_PRICE, reply_markup=back_keyboard)


async def set_usluga_price(message: types.Message, state: FSMContext) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        await state.set_state(UslugiActions.set_name)
        await message.answer(messages.SET_USLUGA_NAME, reply_markup=back_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=main_keyboard)
    else:
        possible_price = validate_usluga_price(text)
        if isinstance(possible_price, int):
            await state.update_data({"price": possible_price})
            await state.set_state(UslugiActions.set_duration)
            await message.answer(messages.SET_USLUGA_DURATION, reply_markup=back_keyboard)
        else:
            error_message = possible_price
            await message.answer(error_message, reply_markup=back_keyboard)


async def set_usluga_duration(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    text = message.text.strip()
    upper_text = text.upper()
    if upper_text == BACK.upper():
        await state.set_state(UslugiActions.set_price)
        await message.answer(messages.SET_USLUGA_PRICE, reply_markup=back_keyboard)
    elif upper_text == MAIN_MENU.upper():
        await state.clear()
        await message.answer(messages.MAIN_MENU, reply_markup=main_keyboard)
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
            await message.answer(error_message, reply_markup=back_keyboard)


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
        await message.answer(messages.MAIN_MENU, reply_markup=main_keyboard)
    else:
        uslugi_to_delete = await state.get_data()
        pos_to_delete = text
        usluga_name_to_delete = uslugi_to_delete.get(pos_to_delete)
        if usluga_name_to_delete is None:
            await message.answer(
                messages.CHOOSE_USLUGA_TO_DELETE,
                reply_markup=back_keyboard,
            )
        else:
            await delete_usluga(async_session, usluga_name_to_delete)
            await state.set_state(UslugiActions.choose_action)
            await state.set_data({})
            await message.answer(
                messages.USLUGA_DELETED.format(name=usluga_name_to_delete),
                reply_markup=uslugi_keyboard,
            )
