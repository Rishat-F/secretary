"""Конфигурационный файл."""

import os

current_dir = os.path.dirname(__file__)
target_dir = os.path.dirname(current_dir)
db_abs_path = os.path.join(target_dir, "secretary.db")

db_url = f"sqlite+aiosqlite:///{db_abs_path}"

ADMIN_TG_ID = int(os.environ["ADMIN_TG_ID"])
