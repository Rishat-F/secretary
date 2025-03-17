from aiogram import Dispatcher, F
from aiogram.enums import ChatType

from handlers import (
    choose_day_to_zapis,
    choose_month_to_zapis,
    choose_time_to_zapis,
    choose_usluga_field_to_update,
    choose_usluga_to_delete,
    choose_usluga_to_update,
    choose_usluga_to_zapis,
    choose_uslugi_action,
    choose_year_to_zapis,
    choose_zapisi_action,
    set_usluga_duration,
    set_usluga_name,
    set_usluga_new_duration,
    set_usluga_new_name,
    set_usluga_new_price,
    set_usluga_price,
    start_bot,
    uslugi,
    zapisi,
)
from keyboards import USLUGI, ZAPISI
from secrets import ADMIN_TG_ID
from states import UslugiActions, ZapisNaPriem


def register_handlers(dp: Dispatcher) -> None:
    """Регистрация обработчиков."""
    dp.message.register(
        choose_zapisi_action,
        F.chat.id != ADMIN_TG_ID,
        ZapisNaPriem.choose_action,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_usluga_to_zapis,
        F.chat.id != ADMIN_TG_ID,
        ZapisNaPriem.choose_usluga,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_year_to_zapis,
        F.chat.id != ADMIN_TG_ID,
        ZapisNaPriem.choose_year,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_month_to_zapis,
        F.chat.id != ADMIN_TG_ID,
        ZapisNaPriem.choose_month,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_day_to_zapis,
        F.chat.id != ADMIN_TG_ID,
        ZapisNaPriem.choose_day,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_time_to_zapis,
        F.chat.id != ADMIN_TG_ID,
        ZapisNaPriem.choose_time,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_uslugi_action,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.choose_action,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_usluga_name,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.set_name,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_usluga_price,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.set_price,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_usluga_duration,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.set_duration,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_usluga_to_delete,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.choose_usluga_to_delete,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_usluga_to_update,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.choose_usluga_to_update,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        choose_usluga_field_to_update,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.choose_usluga_field_to_update,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_usluga_new_name,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.set_new_name,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_usluga_new_price,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.set_new_price,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        set_usluga_new_duration,
        F.chat.id == ADMIN_TG_ID,
        UslugiActions.set_new_duration,
        F.chat.type == ChatType.PRIVATE.value,
    )
    dp.message.register(
        start_bot,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower().contains("/start"),
    )
    dp.message.register(
        uslugi,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower() == USLUGI.lower(),
    )
    dp.message.register(
        zapisi,
        F.chat.type == ChatType.PRIVATE.value,
        F.text.lower() == ZAPISI.lower(),
    )
