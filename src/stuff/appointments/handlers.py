from datetime import datetime, time, timedelta

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src import messages
from src.config import TIMEZONE
from src.database import get_available_slots, get_services, insert_appointment, insert_reservations
from src.models import Appointment
from src.secrets import ADMIN_TG_ID
from src.stuff.appointments.exceptions import (
    DateTimeBecomeNotAvailable,
    DayBecomeNotAvailable,
    MonthBecomeNotAvailable,
    YearBecomeNotAvailable,
)
from src.stuff.appointments.logic import (
    choose_appointments_action_logic,
    choose_service_for_appointment_logic,
)
from src.stuff.appointments.states import MakeAppointment
from src.stuff.appointments.keyboards import (
    AppointmentDateTimePicker,
    appointments_keyboard,
    get_confirm_appointment_keyboard,
    get_days_keyboard,
    get_months_keyboard,
    get_times_keyboard,
    get_years_keyboard,
)
from src.stuff.appointments.utils import (
    check_chosen_datetime_is_possible,
    get_datetimes_needed_for_appointment,
    get_days_keyboard_buttons,
    get_months_keyboard_buttons,
    get_times_keyboard_buttons,
    get_times_possible_for_appointment,
    get_years_keyboard_buttons,
)
from src.stuff.common.handlers import process_logic_return
from src.stuff.common.utils import (
    dates_to_lang,
    form_appointment_view,
    from_utc,
    get_utc_now,
    get_years_with_months,
    get_years_with_months_days,
    to_utc,
)


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
    await process_logic_return(result, fsm_context=state, message=message)


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
    await process_logic_return(result, fsm_context=state, message=message)


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
    months_keyboard_buttons = get_months_keyboard_buttons(
        years_with_months,
        tz_now,
        chosen_year,
    )
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
    days_keyboard_buttons = get_days_keyboard_buttons(
        years_with_months_days,
        tz_now,
        chosen_year,
        chosen_month,
    )
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
            lang_day_month_year=dates_to_lang(chosen_year, chosen_month, chosen_day),
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
                try:
                    await callback.message.delete()
                except TelegramBadRequest:  # давние сообщения удалять нельзя
                    pass
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
                await state.set_state(state_to_set)
                await callback.message.edit_text(text=message_to_edit_to, reply_markup=keyboard_to_show)
                await callback.answer(str(err), show_alert=True)
        else:
            try:
                await callback.message.delete()
            except TelegramBadRequest:  # давние сообщения удалять нельзя
                pass
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


async def cancel_choose_date_for_appointment(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    try:
        await callback.message.delete()
    except TelegramBadRequest:  # давние сообщения удалять нельзя
        pass
    await callback.message.answer(
        text=messages.CANCELED,
        reply_markup=appointments_keyboard,
    )
    await state.set_data({})
    await state.set_state(MakeAppointment.choose_action)
    await callback.answer()
