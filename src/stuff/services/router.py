from aiogram import F, Router
from aiogram.enums import ChatType

from src.secrets import ADMIN_TG_ID
from src.stuff.services.handlers import (
    choose_service_field_to_update,
    choose_service_to_delete,
    choose_service_to_update,
    choose_services_action,
    set_service_duration,
    set_service_name,
    set_service_new_duration,
    set_service_new_name,
    set_service_new_price,
    set_service_price,
)
from src.stuff.services.states import ServicesActions


router = Router()


router.message.register(
    choose_services_action,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.choose_action,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    set_service_name,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.set_name,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    set_service_price,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.set_price,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    set_service_duration,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.set_duration,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    choose_service_to_delete,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.choose_service_to_delete,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    choose_service_to_update,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.choose_service_to_update,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    choose_service_field_to_update,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.choose_service_field_to_update,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    set_service_new_name,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.set_new_name,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    set_service_new_price,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.set_new_price,
    F.chat.type == ChatType.PRIVATE.value,
)
router.message.register(
    set_service_new_duration,
    F.chat.id == ADMIN_TG_ID,
    ServicesActions.set_new_duration,
    F.chat.type == ChatType.PRIVATE.value,
)
