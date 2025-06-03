from aiogram import F, Router
from aiogram.enums import ChatType

from src.secrets import ADMIN_TG_ID
from src.stuff.main_menu.handlers import (
    schedule,
    services,
    start_bot,
    appointments,
)
from src.stuff.main_menu.keyboards import SCHEDULE, USLUGI, ZAPISI


router = Router()

router.message.register(
    start_bot,
    F.chat.type == ChatType.PRIVATE.value,
    F.text.lower().contains("/start"),
)
router.message.register(
    services,
    F.chat.type == ChatType.PRIVATE.value,
    F.text.lower() == USLUGI.lower(),
)
router.message.register(
    appointments,
    F.chat.type == ChatType.PRIVATE.value,
    F.text.lower() == ZAPISI.lower(),
)
router.message.register(
    schedule,
    F.chat.id == ADMIN_TG_ID,
    F.chat.type == ChatType.PRIVATE.value,
    F.text.lower() == SCHEDULE.lower(),
)
