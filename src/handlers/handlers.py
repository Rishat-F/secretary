"""Обработчики бота."""

from datetime import datetime, time, timedelta
from typing import Any

from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src import messages
from src.exceptions import (
    DateTimeBecomeNotAvailable,
    DayBecomeNotAvailable,
    MonthBecomeNotAvailable,
    YearBecomeNotAvailable,
)
from src.business_logic.get_times_possible_for_appointment import get_times_possible_for_appointment
from src.business_logic.resolve_times_status import resolve_times_statuses
from src.business_logic.utils import (
    check_chosen_datetime_is_possible,
    get_datetimes_needed_for_appointment,
    get_days_keyboard_buttons,
    get_months_keyboard_buttons,
    get_set_working_hours_keyboard_buttons,
    get_times_statuses_view,
    get_years_keyboard_buttons,
    get_times_keyboard_buttons,
    get_years_with_months,
    get_years_with_months_days,
)
from src.models import Appointment
from src.handlers.logic import (
    LogicResult,
    alert_not_available_to_choose_logic,
    choose_service_field_to_update_logic,
    choose_service_to_delete_logic,
    choose_service_to_update_logic,
    choose_service_for_appointment_logic,
    choose_services_action_logic,
    choose_appointments_action_logic,
    schedule_logic,
    set_service_duration_logic,
    set_service_name_logic,
    set_service_new_duration_logic,
    set_service_new_name_logic,
    set_service_new_price_logic,
    set_service_price_logic,
    services_logic,
    appointments_logic,
)
from src.config import TIMEZONE
from src.database import (
    get_available_slots,
    get_services,
    insert_appointment,
    insert_reservations,
)
from src.keyboards import (
    ScheduleDateTimePicker,
    appointments_keyboard,
    get_confirm_appointment_keyboard,
    get_days_keyboard,
    get_months_keyboard,
    get_set_working_hours_keyboard,
    get_times_keyboard,
    get_years_keyboard,
    main_keyboard,
    AppointmentDateTimePicker,
)
from src.secrets import ADMIN_TG_ID
from src.states import MakeAppointment
from src.utils import (
    date_to_lang,
    form_appointment_view,
    from_utc,
    get_utc_now,
    to_utc,
)


async def _process_logic_return(
    logic_result: LogicResult,
    fsm_context: FSMContext,
    message: types.Message,
    bot: Bot | None = None,
) -> Any:
    if logic_result.clear_state:
        await fsm_context.clear()
    else:
        if logic_result.state_to_set:
            await fsm_context.set_state(logic_result.state_to_set)
        if isinstance(logic_result.data_to_set, dict):
            await fsm_context.set_data(logic_result.data_to_set)
        if isinstance(logic_result.data_to_update, dict):
            await fsm_context.update_data(logic_result.data_to_update)
    for message_to_answer in logic_result.messages_to_answer:
        await message.answer(
            message_to_answer.text,
            reply_markup=message_to_answer.keyboard,
        )
    if bot:
        for message_to_send in logic_result.messages_to_send:
            await bot.send_message(message_to_send.user_id, message_to_send.text)


async def start_bot(message: types.Message):
    await message.answer(messages.GREETING, reply_markup=main_keyboard)


async def services(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    async with async_session() as session:
        result = await services_logic(user_id=message.from_user.id, session=session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_services_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.text is None:
        return None
    async with async_session() as session:
        result = await choose_services_action_logic(message.text, session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_service_name(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.text is None:
        return None
    async with async_session() as session:
        result = await set_service_name_logic(message.text, session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_service_price(message: types.Message, state: FSMContext) -> None:
    if not message.text:
        return None
    result = await set_service_price_logic(message.text)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_service_duration(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_service_duration_logic(message.text, session, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_service_to_delete(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    services_to_delete = await state.get_data()
    async with async_session() as session:
        result = await choose_service_to_delete_logic(message.text, session, services_to_delete)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_service_to_update(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    services_names = data["services_names"]
    async with async_session() as session:
        result = await choose_service_to_update_logic(message.text, session, services_names)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_service_field_to_update(
    message: types.Message,
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    services_names = data["services_names"]
    result = await choose_service_field_to_update_logic(message.text, services_names)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_service_new_name(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_service_new_name_logic(message.text, session, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_service_new_price(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_service_new_price_logic(message.text, session, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def set_service_new_duration(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await set_service_new_duration_logic(message.text, session, data)
    await _process_logic_return(result, fsm_context=state, message=message)


async def appointments(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    async with async_session() as session:
        result = await appointments_logic(user_id=message.from_user.id, session=session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_appointments_action(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text or not message.from_user:
        return None
    async with async_session() as session:
        result = await choose_appointments_action_logic(
            message.text,
            message.from_user.id,
            session=session,
        )
    await _process_logic_return(result, fsm_context=state, message=message)


async def choose_service_for_appointment(
    message: types.Message,
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if not message.text:
        return None
    data = await state.get_data()
    async with async_session() as session:
        result = await choose_service_for_appointment_logic(message.text, data, session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def go_to_choose_year_for_appointment(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    times_dict = data["times_dict"]
    years = list(times_dict.keys())
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    years_keyboard_buttons = get_years_keyboard_buttons(years, tz_now)
    await state.set_state(MakeAppointment.choose_year)
    await callback.message.edit_text(
        text=messages.CHOOSE_YEAR,
        reply_markup=get_years_keyboard(years_keyboard_buttons),
    )
    await callback.answer()


async def go_to_choose_month_for_appointment(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    times_dict = data["times_dict"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    years_with_months = get_years_with_months(times_dict)
    months_keyboard_buttons = get_months_keyboard_buttons(years_with_months, tz_now, chosen_year)
    await state.set_state(MakeAppointment.choose_month)
    await callback.message.edit_text(
        text=messages.CHOOSE_MONTH,
        reply_markup=get_months_keyboard(chosen_year, months_keyboard_buttons),
    )
    await callback.answer()


async def go_to_choose_day_for_appointment(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    times_dict = data["times_dict"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    chosen_month = callback_data.month
    years_with_months_days = get_years_with_months_days(times_dict)
    days_keyboard_buttons = get_days_keyboard_buttons(years_with_months_days, tz_now, chosen_year, chosen_month)
    await state.set_state(MakeAppointment.choose_day)
    await callback.message.edit_text(
        text=messages.CHOOSE_DAY,
        reply_markup=get_days_keyboard(chosen_year, chosen_month, days_keyboard_buttons),
    )
    await callback.answer()


async def go_to_choose_time_for_appointment(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    times_dict = data["times_dict"]
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
    await state.set_state(MakeAppointment.choose_time)
    await callback.message.edit_text(
        text=messages.CHOOSE_TIME,
        reply_markup=get_times_keyboard(
            chosen_year,
            chosen_month,
            chosen_day,
            times_keyboard_buttons,
        ),
    )
    await callback.answer()


async def go_to_confirm_appointment(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    chosen_service_name = data["chosen_service_name"]
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
    await state.set_state(MakeAppointment.confirm)
    await callback.message.edit_text(
        text=messages.CONFIRM_APPOINTMENT.format(
            lang_day_month_year=date_to_lang(chosen_year, chosen_month, chosen_day),
            time=chosen_time.isoformat(timespec="minutes"),
            service_name=chosen_service_name,
        ),
        reply_markup=get_confirm_appointment_keyboard(chosen_datetime),
    )
    await callback.answer()


async def appointment_confirmed(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    chosen_service_name = data["chosen_service_name"]
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
                await state.set_data({})
                await state.set_state(MakeAppointment.choose_action)
                await callback.message.delete()
                await callback.message.answer(
                    text=messages.NO_POSSIBLE_TIMES_FOR_SERVICE,
                    reply_markup=appointments_keyboard,
                )
                return None
            await state.update_data({"times_dict": times_dict})
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
                    months_keyboard_buttons = get_months_keyboard_buttons(years_with_months, tz_now, chosen_year)
                    keyboard_to_show = get_months_keyboard(chosen_year, months_keyboard_buttons)
                elif isinstance(err, DayBecomeNotAvailable):
                    state_to_set = MakeAppointment.choose_day
                    message_to_edit_to = messages.CHOOSE_DAY
                    years_with_months_days = get_years_with_months_days(times_dict)
                    days_keyboard_buttons = get_days_keyboard_buttons(years_with_months_days, tz_now, chosen_year, chosen_month)
                    keyboard_to_show = get_days_keyboard(chosen_year, chosen_month, days_keyboard_buttons)
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
                await state.set_state(state_to_set)
                await callback.message.edit_text(text=message_to_edit_to, reply_markup=keyboard_to_show)
                await callback.answer(str(err), show_alert=True)
        else:
            await callback.message.delete()
            await session.refresh(appointment)
            await callback.message.answer(
                text=(
                    f"{messages.APPOINTMENT_SAVED}\n"
                    f"{messages.COME.format(appointment_view=form_appointment_view(appointment, with_date=True, for_admin=False))}"
                ),
                reply_markup=appointments_keyboard,
            )
            await session.commit()
            await callback.bot.send_message(
                ADMIN_TG_ID,
                messages.NEW_APPOINTMENT_CREATED.format(
                    appointment_view=form_appointment_view(appointment, with_date=True, for_admin=True),
                ),
            )
            await state.set_data({})
            await state.set_state(MakeAppointment.choose_action)
            await callback.answer(messages.APPOINTMENT_SAVED, show_alert=True)


async def alert_not_available_to_choose(
    callback: types.CallbackQuery,
    callback_data: AppointmentDateTimePicker,
) -> None:
    alert_text = alert_not_available_to_choose_logic(callback_data)
    await callback.answer(alert_text, show_alert=True)


async def ignore_inline_button(callback: types.CallbackQuery) -> None:
    await callback.answer()


async def cancel_choose_date_for_appointment(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    await callback.message.delete()
    await callback.message.answer(
        text=messages.CANCELED,
        reply_markup=appointments_keyboard,
    )
    await state.set_data({})
    await state.set_state(MakeAppointment.choose_action)
    await callback.answer()


async def schedule(
    message: types.Message,
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    result = schedule_logic()
    await _process_logic_return(result, fsm_context=state, message=message)


async def time_clicked(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: ScheduleDateTimePicker,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    times_statuses = data["times_statuses"]
    times_statuses = resolve_times_statuses(times_statuses, callback_data.index)
    times_statuses_view = get_times_statuses_view(times_statuses)
    set_working_hours_keyboard_buttons = get_set_working_hours_keyboard_buttons(times_statuses)
    await callback.message.edit_text(
        text=messages.SET_WORKING_HOURS.format(times_statuses_view=times_statuses_view),
        reply_markup=get_set_working_hours_keyboard(set_working_hours_keyboard_buttons),
    )
    await callback.answer()


async def cancel_set_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    await callback.message.delete()
    await callback.message.answer(
        text=messages.CANCELED,
        reply_markup=main_keyboard,
    )
    await state.clear()
    await callback.answer()
