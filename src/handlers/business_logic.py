from src.models import Service, Slot
from src.utils import get_times_for_appointment


async def get_times_possible_for_appointment(
    service: Service,
    slots: list[Slot],
) -> dict[int, dict[int, dict[int, list[str]]]]:
    """
    Получение доступных времен для записи.

    Возвращается словарь вида:
    {
        2024: {
            12: {
                29: ["10:00", "10:30", "14:30"],
                30: ["08:30", "11:00", "19:00", "19:30"],
            },
        2025: {
            2: {
                26: ["10:00", "10:30", "14:30"],
                27: ["08:30", "11:00", "19:00", "19:30],
                28: ["16:00"],
            },
            3: {
                1: ["10:00", "10:30", "14:30"],
                2: ["08:30", "11:00", "19:00", "19:30],
                3: ["16:00"],
            },
        },
    }
    """
    slots_dict = {}
    for slot in slots:
        if slot.datetime_.year not in slots_dict:
            slots_dict[slot.datetime_.year] = {}
        if slot.datetime_.month not in slots_dict[slot.datetime_.year]:
            slots_dict[slot.datetime_.year][slot.datetime_.month] = {}
        if slot.datetime_.day not in slots_dict[slot.datetime_.year][slot.datetime_.month]:
            slots_dict[slot.datetime_.year][slot.datetime_.month][slot.datetime_.day] = []
        slots_dict[slot.datetime_.year][slot.datetime_.month][slot.datetime_.day].append(slot.datetime_)
    times_dict = {}
    for year_ in slots_dict:
        for month_ in slots_dict[year_]:
            for day_ in slots_dict[year_][month_]:
                slots_datetimes_ = slots_dict[year_][month_][day_]
                times_for_appointment = get_times_for_appointment(
                    slots_datetimes_,
                    service.duration,
                )
                if times_for_appointment:
                    if year_ not in times_dict:
                        times_dict[year_] = {}
                    if month_ not in times_dict[year_]:
                        times_dict[year_][month_] = {}
                    if day_ not in times_dict[year_][month_]:
                        times_dict[year_][month_][day_] = times_for_appointment
    return times_dict
