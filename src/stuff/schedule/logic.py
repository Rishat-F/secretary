from datetime import datetime

from aiogram import types
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src import messages
from src.config import TIMEZONE
from src.constraints import DURATION_MULTIPLIER
from src.database import (
    delete_not_booked_future_slots,
    delete_slots,
    get_future_slots,
    get_slots_by_date,
)
from src.models import Slot
from src.stuff.base.logic import LogicResult, MessageToAnswer, get_logic_result
from src.stuff.common.utils import (
    dates_to_lang,
    from_utc,
    get_utc_now,
    get_years_with_months,
    get_years_with_months_days,
)
from src.stuff.schedule.keyboards import (
    DELETE,
    SAVE,
    Schedule,
    get_confirm_clear_schedule_keyboard,
    set_schedule_get_days_keyboard,
    set_schedule_get_months_keyboard,
    set_schedule_get_times_keyboard,
    set_schedule_get_years_keyboard,
    view_schedule_get_days_keyboard,
    view_schedule_get_months_keyboard,
    view_schedule_get_times_keyboard,
    view_schedule_get_years_keyboard,
)
from src.stuff.schedule.states import ScheduleStates
from src.stuff.schedule.utils import (
    get_days_statuses,
    get_initial_times_statuses,
    get_schedule,
    get_selected_and_not_selected_dates,
    get_selected_dates_view,
    get_selected_times,
    get_slots_to_delete,
    get_slots_to_save,
    get_times_statuses_view,
    get_working_hours_view,
    resolve_days_statuses,
    resolve_times_statuses,
    set_schedule_get_days_keyboard_buttons,
    set_schedule_get_months_keyboard_buttons,
    set_schedule_get_times_keyboard_buttons,
    set_schedule_get_years_keyboard_buttons,
    view_schedule_get_days_keyboard_buttons,
    view_schedule_get_months_keyboard_buttons,
    view_schedule_get_times_keyboard_buttons,
    view_schedule_get_years_keyboard_buttons,
)


def schedule_modifying_logic() -> LogicResult:
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    selected_dates = []
    days_statuses = get_days_statuses(tz_now, selected_dates, None, None)
    times_statuses = get_initial_times_statuses()
    days_keyboard_buttons = set_schedule_get_days_keyboard_buttons(days_statuses)
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    state_to_set = ScheduleStates.set_working_days
    data_to_set = {
        "selected_dates": selected_dates,
        "days_statuses": days_statuses,
        "times_statuses": times_statuses,
    }
    messages_to_answer = [
        MessageToAnswer(
            text=messages.HOW_TO_MODIFY_SCHEDULE.format(
                save_button=SAVE,
                delete_button=DELETE,
            ),
            keyboard=types.ReplyKeyboardRemove(),
        ),
        MessageToAnswer(
            text=f"{selected_dates_view}\n\n{times_statuses_view}",
            keyboard=set_schedule_get_days_keyboard(tz_now.year, tz_now.month, days_keyboard_buttons),
        ),
    ]
    return get_logic_result(
        messages_to_answer=messages_to_answer,
        state_to_set=state_to_set,
        data_to_set=data_to_set,
    )


def go_to_choose_year_for_set_schedule_logic(state_data: dict) -> LogicResult:
    selected_dates = state_data["selected_dates"]
    times_statuses = state_data["times_statuses"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    years_keyboard_buttons = set_schedule_get_years_keyboard_buttons(tz_now)
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    state_to_set = ScheduleStates.choose_year
    edit_message = MessageToAnswer(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        keyboard=set_schedule_get_years_keyboard(years_keyboard_buttons),
    )
    return get_logic_result(edit_message=edit_message, state_to_set=state_to_set)


def go_to_choose_month_for_set_schedule_logic(
    state_data: dict,
    callback_data: Schedule,
) -> LogicResult:
    selected_dates = state_data["selected_dates"]
    times_statuses = state_data["times_statuses"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    months_keyboard_buttons = set_schedule_get_months_keyboard_buttons(
        tz_now,
        chosen_year,
    )
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    state_to_set = ScheduleStates.choose_month
    edit_message = MessageToAnswer(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        keyboard=set_schedule_get_months_keyboard(chosen_year, months_keyboard_buttons),
    )
    return get_logic_result(edit_message=edit_message, state_to_set=state_to_set)


def go_to_set_working_days_logic(
    state_data: dict,
    callback_data: Schedule,
) -> LogicResult:
    selected_dates = state_data["selected_dates"]
    times_statuses = state_data["times_statuses"]
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
    state_to_set = ScheduleStates.set_working_days
    data_to_update = {"days_statuses": days_statuses}
    edit_message = MessageToAnswer(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        keyboard=set_schedule_get_days_keyboard(chosen_year, chosen_month, days_keyboard_buttons),
    )
    return get_logic_result(
        edit_message=edit_message,
        state_to_set=state_to_set,
        data_to_update=data_to_update,
    )


def go_to_set_working_hours_logic(state_data: dict) -> LogicResult:
    selected_dates = state_data["selected_dates"]
    times_statuses = state_data["times_statuses"]
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses_view = get_times_statuses_view(times_statuses)
    times_keyboard_buttons = set_schedule_get_times_keyboard_buttons(times_statuses)
    state_to_set = ScheduleStates.set_working_hours
    data_to_update = {"times_statuses": times_statuses}
    edit_message = MessageToAnswer(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        keyboard=set_schedule_get_times_keyboard(times_keyboard_buttons),
    )
    return get_logic_result(
        edit_message=edit_message,
        state_to_set=state_to_set,
        data_to_update=data_to_update,
    )


def day_clicked_logic(
    state_data: dict,
    callback_data: Schedule,
) -> LogicResult:
    days_statuses = state_data["days_statuses"]
    selected_dates = state_data["selected_dates"]
    times_statuses = state_data["times_statuses"]
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
    data_to_update = {"selected_dates": selected_dates, "days_statuses": days_statuses}
    edit_message = MessageToAnswer(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        keyboard=set_schedule_get_days_keyboard(
            callback_data.year,
            callback_data.month,
            days_keyboard_buttons,
        ),
    )
    return get_logic_result(edit_message=edit_message, data_to_update=data_to_update)


def time_clicked_logic(
    state_data: dict,
    callback_data: Schedule,
) -> LogicResult:
    selected_dates = state_data["selected_dates"]
    selected_dates_view = get_selected_dates_view(selected_dates)
    times_statuses = state_data["times_statuses"]
    times_statuses = resolve_times_statuses(times_statuses, callback_data.index)
    times_statuses_view = get_times_statuses_view(times_statuses)
    times_keyboard_buttons = set_schedule_get_times_keyboard_buttons(times_statuses)
    edit_message = MessageToAnswer(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        keyboard=set_schedule_get_times_keyboard(times_keyboard_buttons),
    )
    return get_logic_result(edit_message=edit_message)


async def save_schedule_logic(
    state_data: dict,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    selected_dates = state_data["selected_dates"]
    times_statuses = state_data["times_statuses"]
    selected_times = get_selected_times(times_statuses)
    if not selected_dates:
        alert_text = messages.SELECT_WORKING_DATES
        result = get_logic_result(alert_text=alert_text)
    elif not selected_times:
        alert_text = messages.SELECT_WORKING_HOURS
        result = get_logic_result(alert_text=alert_text)
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
        state_to_set = ScheduleStates.set_working_days
        data_to_update = {
            "selected_dates": selected_dates,
            "times_statuses": times_statuses,
            "days_statuses": days_statuses,
        }
        edit_message = MessageToAnswer(
            text=f"{selected_dates_view}\n\n{times_statuses_view}",
            keyboard=set_schedule_get_days_keyboard(
                tz_now.year,
                tz_now.month,
                days_keyboard_buttons,
            ),
        )
        alert_text = messages.SCHEDULE_MODIFIED
        result = get_logic_result(
            edit_message=edit_message,
            state_to_set=state_to_set,
            data_to_update=data_to_update,
            alert_text=alert_text,
        )
    return result


async def delete_schedule_logic(
    state_data: dict,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    selected_dates = state_data["selected_dates"]
    times_statuses = state_data["times_statuses"]
    selected_times = get_selected_times(times_statuses)
    if not selected_dates:
        alert_text = messages.SELECT_WORKING_DATES
        return get_logic_result(alert_text=alert_text)
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
    state_to_set = ScheduleStates.set_working_days
    data_to_update = {
        "selected_dates": selected_dates,
        "times_statuses": times_statuses,
        "days_statuses": days_statuses,
    }
    edit_message = MessageToAnswer(
        text=f"{selected_dates_view}\n\n{times_statuses_view}",
        keyboard=set_schedule_get_days_keyboard(
            tz_now.year,
            tz_now.month,
            days_keyboard_buttons,
        ),
    )
    alert_text = messages.SCHEDULE_MODIFIED
    return get_logic_result(
        edit_message=edit_message,
        state_to_set=state_to_set,
        data_to_update=data_to_update,
        alert_text=alert_text,
    )


def clear_schedule_clicked_logic() -> LogicResult:
    state_to_set = ScheduleStates.confirm_schedule_clear
    edit_message = MessageToAnswer(
        text=messages.CLEAR_SCHEDULE_WARNING,
        keyboard=get_confirm_clear_schedule_keyboard(),
    )
    return get_logic_result(edit_message=edit_message, state_to_set=state_to_set)


async def clear_schedule_confirmed_logic(
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    utc_now = get_utc_now()
    async with async_session() as session:
        await delete_not_booked_future_slots(session, utc_now)
        await session.commit()
    alert_text = messages.SCHEDULE_CLEARED
    return get_logic_result(alert_text=alert_text)


def go_to_choose_year_while_view_schedule_logic(state_data: dict) -> LogicResult:
    schedule_dict = state_data["schedule_dict"]
    years = list(schedule_dict.keys())
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    years_keyboard_buttons = view_schedule_get_years_keyboard_buttons(years, tz_now)
    edit_message = MessageToAnswer(
        text=messages.SCHEDULE_VIEW,
        keyboard=view_schedule_get_years_keyboard(years_keyboard_buttons),
    )
    return get_logic_result(edit_message=edit_message)


def go_to_choose_month_while_view_schedule_logic(
    state_data: dict,
    callback_data: Schedule,
) -> LogicResult:
    schedule_dict = state_data["schedule_dict"]
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    chosen_year = callback_data.year
    years_with_months = get_years_with_months(schedule_dict)
    months_keyboard_buttons = view_schedule_get_months_keyboard_buttons(
        years_with_months,
        tz_now,
        chosen_year,
    )
    edit_message = MessageToAnswer(
        text=messages.SCHEDULE_VIEW,
        keyboard=view_schedule_get_months_keyboard(chosen_year, months_keyboard_buttons),
    )
    return get_logic_result(edit_message=edit_message)


async def go_to_choose_day_while_view_schedule_logic(
    callback_data: Schedule,
    async_session: async_sessionmaker[AsyncSession],
) -> LogicResult:
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    async with async_session() as session:
        slots = await get_future_slots(session, utc_now)
    schedule_dict = get_schedule(slots)
    if not schedule_dict:
        edit_message = MessageToAnswer(
            text=messages.NO_SCHEDULE,
            keyboard=view_schedule_get_days_keyboard(0, 0, []),
        )
    else:
        years_with_months_days = get_years_with_months_days(schedule_dict)
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
        edit_message = MessageToAnswer(
            text=messages.SCHEDULE_VIEW,
            keyboard=view_schedule_get_days_keyboard(chosen_year, chosen_month, days_keyboard_buttons),
        )
    state_to_set = ScheduleStates.view_schedule
    data_to_update = {"schedule_dict": schedule_dict}
    return get_logic_result(
        edit_message=edit_message,
        state_to_set=state_to_set,
        data_to_update=data_to_update,
    )


def show_working_hours_logic(
    state_data: dict,
    callback_data: Schedule,
) -> LogicResult:
    schedule_dict = state_data["schedule_dict"]
    chosen_year = callback_data.year
    chosen_month = callback_data.month
    chosen_day = callback_data.day
    date_lang = dates_to_lang(chosen_year, chosen_month, chosen_day)
    iso_working_hours = schedule_dict[chosen_year][chosen_month][chosen_day]
    working_hours_view = get_working_hours_view(iso_working_hours, DURATION_MULTIPLIER)
    alert_text = f"{date_lang}\n\n{working_hours_view}"
    return get_logic_result(alert_text=alert_text)


def show_working_hours_in_inline_mode_logic(
    state_data: dict,
    callback_data: Schedule,
) -> LogicResult:
    schedule_dict = state_data["schedule_dict"]
    chosen_year = callback_data.year
    chosen_month = callback_data.month
    chosen_day = callback_data.day
    utc_now = get_utc_now()
    tz_now = from_utc(utc_now, TIMEZONE)
    times_keyboard_buttons = view_schedule_get_times_keyboard_buttons(
        schedule_dict,
        tz_now,
        chosen_year,
        chosen_month,
        chosen_day,
    )
    edit_message = MessageToAnswer(
        text=messages.SCHEDULE_VIEW,
        keyboard=view_schedule_get_times_keyboard(
            chosen_year,
            chosen_month,
            chosen_day,
            times_keyboard_buttons,
        ),
    )
    return get_logic_result(edit_message=edit_message)
