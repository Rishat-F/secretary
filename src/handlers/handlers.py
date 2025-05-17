"""Обработчики бота."""

from datetime import datetime, time, timedelta
from typing import Any

from aiogram import Bot, types
from aiogram.exceptions import TelegramBadRequest
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
from src.business_logic.make_appointment import get_times_possible_for_appointment
from src.business_logic.make_appointment.utils import (
    check_chosen_datetime_is_possible,
    get_datetimes_needed_for_appointment,
    get_years_with_months,
    get_years_with_months_days,
    make_appointment_get_days_keyboard_buttons,
    make_appointment_get_months_keyboard_buttons,
    make_appointment_get_years_keyboard_buttons,
    make_appointment_get_times_keyboard_buttons,
)
from src.business_logic.resolve_days_statuses.resolve_days_statuses import resolve_days_statuses
from src.business_logic.resolve_days_statuses.utils import (
    get_days_statuses,
    get_selected_and_not_selected_dates,
    get_selected_dates_view,
    set_schedule_get_days_keyboard_buttons,
    set_schedule_get_months_keyboard_buttons,
    set_schedule_get_years_keyboard_buttons,
)
from src.business_logic.resolve_times_statuses.resolve_times_statuses import resolve_times_statuses
from src.business_logic.resolve_times_statuses.utils import (
    get_initial_times_statuses,
    get_selected_times,
    get_slots_to_delete,
    get_slots_to_save,
    get_times_statuses_view,
    get_working_hours_view,
    set_schedule_get_times_keyboard_buttons,
)
from src.business_logic.schedule.get_schedule import get_schedule
from src.business_logic.schedule.utils import (
    view_schedule_get_days_keyboard_buttons,
    view_schedule_get_months_keyboard_buttons,
    view_schedule_get_times_keyboard_buttons,
    view_schedule_get_years_keyboard_buttons,
)
from src.constraints import DURATION_MULTIPLIER
from src.models import Appointment, Slot
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
    delete_not_booked_future_slots,
    delete_slots,
    get_available_slots,
    get_future_slots,
    get_services,
    get_slots_by_date,
    insert_appointment,
    insert_reservations,
)
from src.keyboards import (
    DELETE,
    SAVE,
    Schedule,
    appointments_keyboard,
    get_confirm_appointment_keyboard,
    get_confirm_clear_schedule_keyboard,
    main_keyboard,
    AppointmentDateTimePicker,
    make_appointment_get_days_keyboard,
    make_appointment_get_months_keyboard,
    make_appointment_get_times_keyboard,
    make_appointment_get_years_keyboard,
    set_schedule_get_days_keyboard,
    set_schedule_get_months_keyboard,
    set_schedule_get_times_keyboard,
    set_schedule_get_years_keyboard,
    view_schedule_get_days_keyboard,
    view_schedule_get_months_keyboard,
    view_schedule_get_times_keyboard,
    view_schedule_get_years_keyboard,
)
from src.secrets import ADMIN_TG_ID
from src.states import MakeAppointment, ScheduleStates
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
    years_keyboard_buttons = make_appointment_get_years_keyboard_buttons(years, tz_now)
    await state.set_state(MakeAppointment.choose_year)
    await callback.message.edit_text(
        text=messages.CHOOSE_YEAR,
        reply_markup=make_appointment_get_years_keyboard(years_keyboard_buttons),
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
    months_keyboard_buttons = make_appointment_get_months_keyboard_buttons(
        years_with_months,
        tz_now,
        chosen_year,
    )
    await state.set_state(MakeAppointment.choose_month)
    await callback.message.edit_text(
        text=messages.CHOOSE_MONTH,
        reply_markup=make_appointment_get_months_keyboard(chosen_year, months_keyboard_buttons),
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
    days_keyboard_buttons = make_appointment_get_days_keyboard_buttons(
        years_with_months_days,
        tz_now,
        chosen_year,
        chosen_month,
    )
    await state.set_state(MakeAppointment.choose_day)
    await callback.message.edit_text(
        text=messages.CHOOSE_DAY,
        reply_markup=make_appointment_get_days_keyboard(chosen_year, chosen_month, days_keyboard_buttons),
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
    times_keyboard_buttons = make_appointment_get_times_keyboard_buttons(
        times_dict,
        tz_now,
        chosen_year,
        chosen_month,
        chosen_day,
    )
    await state.set_state(MakeAppointment.choose_time)
    await callback.message.edit_text(
        text=messages.CHOOSE_TIME,
        reply_markup=make_appointment_get_times_keyboard(
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
                    years_keyboard_buttons = make_appointment_get_years_keyboard_buttons(years, tz_now)
                    keyboard_to_show = make_appointment_get_years_keyboard(years_keyboard_buttons)
                elif isinstance(err, MonthBecomeNotAvailable):
                    state_to_set = MakeAppointment.choose_month
                    message_to_edit_to = messages.CHOOSE_MONTH
                    years_with_months = get_years_with_months(times_dict)
                    months_keyboard_buttons = make_appointment_get_months_keyboard_buttons(
                        years_with_months,
                        tz_now,
                        chosen_year,
                    )
                    keyboard_to_show = make_appointment_get_months_keyboard(chosen_year, months_keyboard_buttons)
                elif isinstance(err, DayBecomeNotAvailable):
                    state_to_set = MakeAppointment.choose_day
                    message_to_edit_to = messages.CHOOSE_DAY
                    years_with_months_days = get_years_with_months_days(times_dict)
                    days_keyboard_buttons = make_appointment_get_days_keyboard_buttons(
                        years_with_months_days,
                        tz_now,
                        chosen_year,
                        chosen_month,
                    )
                    keyboard_to_show = make_appointment_get_days_keyboard(
                        chosen_year,
                        chosen_month,
                        days_keyboard_buttons,
                    )
                else:
                    state_to_set = MakeAppointment.choose_time
                    message_to_edit_to = messages.CHOOSE_TIME
                    times_keyboard_buttons = make_appointment_get_times_keyboard_buttons(
                        times_dict,
                        tz_now,
                        chosen_year,
                        chosen_month,
                        chosen_day,
                    )
                    keyboard_to_show = make_appointment_get_times_keyboard(
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


async def alert_not_available_to_choose_day(  # ToDo: заменить функцией выше
    callback: types.CallbackQuery,
) -> None:
    alert_text = "Недоступно для выбора"
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
    async_session: async_sessionmaker[AsyncSession],
    state: FSMContext,
) -> None:
    if message.from_user is None:
        return None
    async with async_session() as session:
        result = await schedule_logic(session)
    await _process_logic_return(result, fsm_context=state, message=message)


async def go_to_main_menu_from_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    await callback.message.delete()
    await callback.message.answer(
        text=messages.MAIN_MENU,
        reply_markup=main_keyboard,
    )
    await state.clear()
    await callback.answer()


async def schedule_modifying(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    selected_dates = []
    days_statuses = get_days_statuses(tz_now, selected_dates, None, None)
    times_statuses = get_initial_times_statuses()
    days_keyboard_buttons = set_schedule_get_days_keyboard_buttons(days_statuses)
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    await state.set_state(ScheduleStates.set_working_days)
    await state.set_data(
        {
            "selected_dates": selected_dates,
            "days_statuses": days_statuses,
            "times_statuses": times_statuses,
        }
    )
    await callback.message.delete()
    await callback.message.answer(
        text=messages.HOW_TO_MODIFY_SCHEDULE.format(
            save_button=SAVE,
            delete_button=DELETE,
        ),
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await callback.message.answer(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        reply_markup=set_schedule_get_days_keyboard(tz_now.year, tz_now.month, days_keyboard_buttons),
    )
    await callback.answer()


async def go_to_choose_year_for_set_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    selected_dates = data["selected_dates"]
    times_statuses = data["times_statuses"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    years_keyboard_buttons = set_schedule_get_years_keyboard_buttons(tz_now)
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    await state.set_state(ScheduleStates.choose_year)
    await callback.message.edit_text(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        reply_markup=set_schedule_get_years_keyboard(years_keyboard_buttons),
    )
    await callback.answer()


async def go_to_choose_month_for_set_schedule(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    selected_dates = data["selected_dates"]
    times_statuses = data["times_statuses"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    months_keyboard_buttons = set_schedule_get_months_keyboard_buttons(
        tz_now,
        chosen_year,
    )
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    await state.set_state(ScheduleStates.choose_month)
    await callback.message.edit_text(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        reply_markup=set_schedule_get_months_keyboard(chosen_year, months_keyboard_buttons),
    )
    await callback.answer()


async def go_to_set_working_days(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    selected_dates = data["selected_dates"]
    times_statuses = data["times_statuses"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    chosen_month = callback_data.month
    if not chosen_year:
        chosen_year = tz_now.year
    if not chosen_month:
        chosen_month = tz_now.month
    days_statuses = get_days_statuses(tz_now, selected_dates, chosen_year, chosen_month)
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    days_keyboard_buttons = set_schedule_get_days_keyboard_buttons(days_statuses)
    await state.set_state(ScheduleStates.set_working_days)
    await state.update_data({"days_statuses": days_statuses})
    await callback.message.edit_text(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        reply_markup=set_schedule_get_days_keyboard(chosen_year, chosen_month, days_keyboard_buttons),
    )
    await callback.answer()


async def go_to_set_working_hours(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    selected_dates = data["selected_dates"]
    times_statuses = data["times_statuses"]
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    times_keyboard_buttons = set_schedule_get_times_keyboard_buttons(times_statuses)
    await state.set_state(ScheduleStates.set_working_hours)
    await state.update_data({"times_statuses": times_statuses})
    await callback.message.edit_text(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        reply_markup=set_schedule_get_times_keyboard(times_keyboard_buttons),
    )
    await callback.answer()


async def day_clicked(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: Schedule,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    days_statuses = data["days_statuses"]
    selected_dates = data["selected_dates"]
    times_statuses = data["times_statuses"]
    clicked_element = days_statuses[callback_data.index]
    days_statuses = resolve_days_statuses(days_statuses, clicked_element)
    month_selected_dates, month_not_selected_dates = get_selected_and_not_selected_dates(days_statuses)
    days_keyboard_buttons = set_schedule_get_days_keyboard_buttons(days_statuses)
    for date_ in month_not_selected_dates:
        if date_ in selected_dates:
            selected_dates.remove(date_)
    for date_ in month_selected_dates:
        if date_ not in selected_dates:
            selected_dates.append(date_)
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    await state.update_data(
        {"selected_dates": selected_dates, "days_statuses": days_statuses},
    )
    await callback.message.edit_text(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        reply_markup=set_schedule_get_days_keyboard(
            callback_data.year,
            callback_data.month,
            days_keyboard_buttons,
        ),
    )
    await callback.answer()


async def time_clicked(
    callback: types.CallbackQuery,
    state: FSMContext,
    callback_data: Schedule,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    selected_dates = data["selected_dates"]
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses = data["times_statuses"]
    times_statuses = resolve_times_statuses(times_statuses, callback_data.index)
    times_statuses_view = get_times_statuses_view(times_statuses)
    times_keyboard_buttons = set_schedule_get_times_keyboard_buttons(times_statuses)
    await callback.message.edit_text(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        reply_markup=set_schedule_get_times_keyboard(times_keyboard_buttons),
    )
    await callback.answer()


async def save_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    selected_dates = data["selected_dates"]
    times_statuses = data["times_statuses"]
    selected_times = get_selected_times(times_statuses)
    if not selected_dates:
        await callback.answer(messages.SELECT_WORKING_DATES, show_alert=True)
    elif not selected_times:
        await callback.answer(messages.SELECT_WORKING_HOURS, show_alert=True)
    else:
        async with async_session() as session:
            utc_dates_slots_to_save = get_slots_to_save(selected_dates, selected_times)
            for iso_utc_date, iso_utc_slots_to_save in utc_dates_slots_to_save.items():
                slots_to_delete = await get_slots_by_date(session, iso_utc_date)
                for slot_to_delete in slots_to_delete:
                    try:
                        await session.delete(slot_to_delete)
                        await session.commit()
                    except IntegrityError:
                        await session.rollback()
                for iso_utc_slot in iso_utc_slots_to_save:
                    try:
                        slot = Slot(datetime_=datetime.fromisoformat(iso_utc_slot))
                        session.add(slot)
                        await session.commit()
                    except IntegrityError:
                        await session.rollback()
        selected_dates = []
        utc_now = get_utc_now()
        tz_now = from_utc(utc_now, TIMEZONE)
        days_statuses = get_days_statuses(tz_now, selected_dates, tz_now.year, tz_now.month)
        times_statuses = get_initial_times_statuses()
        selected_dates_view = get_selected_dates_view(selected_dates)
        times_statuses_view = get_times_statuses_view(times_statuses)
        days_keyboard_buttons = set_schedule_get_days_keyboard_buttons(days_statuses)
        await state.set_state(ScheduleStates.set_working_days)
        await state.update_data(
            {
                "selected_dates": selected_dates,
                "times_statuses": times_statuses,
                "days_statuses": days_statuses,
            }
        )
        await callback.message.edit_text(
            text=f"{selected_dates_view}\n\n{times_statuses_view}",
            reply_markup=set_schedule_get_days_keyboard(
                tz_now.year,
                tz_now.month,
                days_keyboard_buttons,
            ),
        )
        await callback.answer(messages.SCHEDULE_MODIFIED, show_alert=True)


async def delete_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    selected_dates = data["selected_dates"]
    times_statuses = data["times_statuses"]
    selected_times = get_selected_times(times_statuses)
    if not selected_dates:
        await callback.answer(messages.SELECT_WORKING_DATES, show_alert=True)
        return None
    if not selected_times:
        async with async_session() as session:
            for iso_date in selected_dates:
                slots_to_delete = await get_slots_by_date(session, iso_date)
                for slot_to_delete in slots_to_delete:
                    try:
                        await session.delete(slot_to_delete)
                        await session.commit()
                    except IntegrityError:
                        await session.rollback()
    else:
        slots_to_delete = get_slots_to_delete(selected_dates, selected_times)
        async with async_session() as session:
            await delete_slots(session, slots_to_delete)
    selected_dates = []
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    days_statuses = get_days_statuses(tz_now, selected_dates, tz_now.year, tz_now.month)
    times_statuses = get_initial_times_statuses()
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    days_keyboard_buttons = set_schedule_get_days_keyboard_buttons(days_statuses)
    await state.set_state(ScheduleStates.set_working_days)
    await state.update_data(
        {
            "selected_dates": selected_dates,
            "times_statuses": times_statuses,
            "days_statuses": days_statuses,
        }
    )
    await callback.message.edit_text(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        reply_markup=set_schedule_get_days_keyboard(
            tz_now.year,
            tz_now.month,
            days_keyboard_buttons,
        ),
    )
    await callback.answer(messages.SCHEDULE_MODIFIED, show_alert=True)


async def clear_schedule_clicked(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    await state.set_state(ScheduleStates.confirm_schedule_clear)
    await callback.message.edit_text(
        text=messages.CLEAR_SCHEDULE_WARNING,
        reply_markup=get_confirm_clear_schedule_keyboard(),
    )
    await callback.answer()


async def clear_schedule_confirmed(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    if not callback.message:
        return None
    utc_now = get_utc_now()
    async with async_session() as session:
        await delete_not_booked_future_slots(session, utc_now)
        await session.commit()
    await callback.message.answer(messages.SCHEDULE_CLEARED)
    await callback.answer(messages.SCHEDULE_CLEARED, show_alert=True)
    await go_to_choose_day_while_view_schedule(callback, callback_data, state, async_session)


async def go_to_choose_year_while_view_schedule(
    callback: types.CallbackQuery,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    schedule_dict = data["schedule_dict"]
    years = list(schedule_dict.keys())
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    years_keyboard_buttons = view_schedule_get_years_keyboard_buttons(years, tz_now)
    await callback.message.edit_text(
        text=messages.SCHEDULE_VIEW,
        reply_markup=view_schedule_get_years_keyboard(years_keyboard_buttons),
    )
    await callback.answer()


async def go_to_choose_month_while_view_schedule(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    schedule_dict = data["schedule_dict"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    years_with_months = get_years_with_months(schedule_dict)
    months_keyboard_buttons = view_schedule_get_months_keyboard_buttons(
        years_with_months,
        tz_now,
        chosen_year,
    )
    await callback.message.edit_text(
        text=messages.SCHEDULE_VIEW,
        reply_markup=view_schedule_get_months_keyboard(chosen_year, months_keyboard_buttons),
    )
    await callback.answer()


async def go_to_choose_day_while_view_schedule(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
    async_session: async_sessionmaker[AsyncSession],
) -> None:
    if not callback.message:
        return None
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    async with async_session() as session:
        slots = await get_future_slots(session, utc_now)
    schedule_dict = get_schedule(slots)
    if not schedule_dict:
        await callback.message.edit_text(
            text=messages.NO_SCHEDULE,
            reply_markup=view_schedule_get_days_keyboard(0, 0, []),
        )
    else:
        years_with_months_days = get_years_with_months_days(schedule_dict)  # ToDo: вынести хелпер в общие
        chosen_year = callback_data.year
        chosen_month = callback_data.month
        if not chosen_year:
            chosen_year = min(years_with_months_days.keys())
        if not chosen_month:
            chosen_month = min(years_with_months_days[chosen_year].keys())
        days_keyboard_buttons = view_schedule_get_days_keyboard_buttons(
            years_with_months_days,
            tz_now,
            chosen_year,
            chosen_month,
        )
        await callback.message.edit_text(
            text=messages.SCHEDULE_VIEW,
            reply_markup=view_schedule_get_days_keyboard(chosen_year, chosen_month, days_keyboard_buttons),
        )
    await state.update_data({"schedule_dict": schedule_dict})
    await state.set_state(ScheduleStates.view_schedule)
    await callback.answer()


async def show_working_hours(
    callback: types.CallbackQuery,
    callback_data: Schedule,
    state: FSMContext,
) -> None:
    if not callback.message:
        return None
    data = await state.get_data()
    schedule_dict = data["schedule_dict"]
    chosen_year = callback_data.year
    chosen_month = callback_data.month
    chosen_day = callback_data.day
    date_lang = date_to_lang(chosen_year, chosen_month, chosen_day)
    iso_working_hours = schedule_dict[chosen_year][chosen_month][chosen_day]
    working_hours_view = get_working_hours_view(iso_working_hours, DURATION_MULTIPLIER)
    text = f"{date_lang}\n\n{working_hours_view}"
    try:
        await callback.answer(text, show_alert=True)
    except TelegramBadRequest:  # слишком длинный текст (более 200 символов)
        utc_now = get_utc_now()
        tz_now = from_utc(utc_now, TIMEZONE)
        times_keyboard_buttons = view_schedule_get_times_keyboard_buttons(
            schedule_dict,
            tz_now,
            chosen_year,
            chosen_month,
            chosen_day,
        )
        await callback.message.edit_text(
            text=messages.SCHEDULE_VIEW,
            reply_markup=view_schedule_get_times_keyboard(
                chosen_year,
                chosen_month,
                chosen_day,
                times_keyboard_buttons,
            ),
        )
        await callback.answer()
