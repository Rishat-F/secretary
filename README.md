# Secretary

Бот-секретарь для организации процесса записи на прием на предоставляемые услуги.

[Рабочая доска проекта](https://github.com/users/Rishat-F/projects/4)

## Разворачивание бота

### 1. Создать бота в Телеграмм

Это делается через официального бота Телеграмма - [@BotFather](https://t.me/BotFather).

### 2. Задать переменные окружения:

- BOT_TOKEN
- ADMIN_TG_ID
- TIMEZONE (например, "Europe/Moscow")

### 3. Запустить бота

Без использования докера:

```console
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.bot
```

С использованием докера:

```console
docker compose up
```

### 4. Остановить бота

Сочетание клавиш ```CTRL+C```
