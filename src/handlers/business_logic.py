from src.models import Service, Slot
from src.utils import get_times_for_appointment


async def get_times_possible_for_appointment(
    service: Service,
    slots: list[Slot],
) -> dict[int, dict[int, dict[int, dict[str, list[int]]]]]:
    """
    Получение доступных времен для записи.

    Возвращается словарь вида:
    {
        2024: {
            12: {
                29: {"10:00": [1, 2], "10:30": [2, 3], "14:30": [3, 4]},
                30: {"08:30": [5, 6], "11:00": [7, 8], "19:00": [9, 10], "19:30": [11, 12]},
            },
        2025: {
            2: {
                26: {"10:00": [13, 14], "10:30": [15, 16], "14:30": [17, 18]},
                27: {"08:30": [19, 20], "11:00": [21, 22], "19:00": [23, 24], "19:30: [25, 26]},
                28: {"16:00": [27, 28]},
            },
            3: {
                1: {"10:00": [29, 30], "10:30": [31, 32], "14:30": [33, 34]},
                2: {"08:30": [35, 36], "11:00": [37, 38], "19:00": [39, 40], "19:30: [41, 42]},
                3: {"16:00": [43, 44]},
            },
        },
    }
    """
    slots_dict = {}
    for slot in slots:
        if slot.date_.year not in slots_dict:
            slots_dict[slot.date_.year] = {}
        if slot.date_.month not in slots_dict[slot.date_.year]:
            slots_dict[slot.date_.year][slot.date_.month] = {}
        if slot.date_.day not in slots_dict[slot.date_.year][slot.date_.month]:
            slots_dict[slot.date_.year][slot.date_.month][slot.date_.day] = []
        slots_dict[slot.date_.year][slot.date_.month][slot.date_.day].append((slot.slot_id, slot.number))
    times_dict = {}
    for year_ in slots_dict:
        for month_ in slots_dict[year_]:
            for day_ in slots_dict[year_][month_]:
                slots_ids_numbers = slots_dict[year_][month_][day_]
                times_for_appointment = get_times_for_appointment(
                    slots_ids_numbers,
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
