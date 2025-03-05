"""Вспомогательные функции."""

from messages import NO_USLUGI
from models import Usluga


def form_uslugi_list_text(uslugi: list[Usluga]) -> str:
    text = ""
    for pos, usluga in enumerate(uslugi, start=1):
        text += (
            f"<b>{pos}. {usluga.name}</b>\n    <i>Стоимость: {usluga.price}</i> руб.\n"
        )
    if not text:
        text = NO_USLUGI
    return text.strip()
