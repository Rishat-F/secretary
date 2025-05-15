"""Сообщения бота."""

GREETING = "Бот готов к работе!"
NO_SERVICES = "На данный момент никаких услуг нет"
NO_SUCH_SERVICE = 'Услуги с названием <b>"{name}"</b> нет'
NO_APPOINTMENTS_FOR_ADMIN = "На данный момент никаких записей нет"
NO_APPOINTMENTS_FOR_CLIENT = "У вас пока нет активных записей"
CHOOSE_ACTION = "Выберите действие"
CHOOSE_GIVEN_ACTION = "Выберите действие из предложенных"
MAIN_MENU = "Главное меню"

SET_SERVICE_NAME = "Задайте название услуги"
SERVICE_ALREADY_EXISTS = 'Услуга с названием <b>"{name}"</b> уже существует!'
SET_SERVICE_PRICE = "Задайте цену услуги в рублях\n(например, 300)"
SET_SERVICE_DURATION = (
    "Задайте длительность услуги в минутах (кратно 30)\n(например, 90)"
)
SERVICE_CREATED = 'Услуга <b>"{name}"</b> создана!'

CHOOSE_SERVICE_TO_UPDATE = "Выберите услугу, которую хотите изменить"
CHOOSE_GIVEN_SERVICES = "Выберите услугу из предложенных"
CHOOSE_FIELD_TO_CHANGE = "Выберите, что хотите изменить"
CHOOSE_GIVEN_FIELD_TO_CHANGE = "Выберите из предложенных"

SET_SERVICE_NEW_NAME = "Задайте новое название услуги"
SERVICE_OLD_NAME_AND_NEW_NAME_ARE_SIMILAR = (
    "Новое название ничем не отличается от старого!"
)
SERVICE_NEW_NAME_SETTLED = 'Название "{old_name}" изменено на <b>"{new_name}"</b>'

SET_SERVICE_NEW_PRICE = "Задайте новую цену услуги"
SERVICE_OLD_PRICE_AND_NEW_PRICE_ARE_SIMILAR = "Новая цена не отличается от старой!"
SERVICE_NEW_PRICE_SETTLED = (
    'Цена услуги <b>"{service_name}"</b> изменена с {old_price} рублей '
    'на <b>{new_price} рублей</b>'
)

SET_SERVICE_NEW_DURATION = "Задайте новую длительность услуги"
SERVICE_OLD_DURATION_AND_NEW_DURATION_ARE_SIMILAR = (
    "Новая длительность не отличается от старой!"
)
SERVICE_NEW_DURATION_SETTLED = (
    'Длительность услуги <b>"{service_name}"</b> изменена с {old_duration} минут '
    'на <b>{new_duration} минут</b>'
)

CHOOSE_SERVICE_TO_DELETE = "Введите порядковый номер услуги, которую хотите удалить"
SERVICE_DELETED = 'Услуга <b>"{name}"</b> удалена!'

CHOOSE_SERVICE_TO_MAKE_APPOINTMENT = "Введите порядковый номер услуги, на которую хотите записаться"
NO_POSSIBLE_TIMES_FOR_SERVICE = 'Времени, доступного для записи на услугу <b>"{name}"</b>, нет'
MAKING_APPOINTMENT = 'Запись на услугу <b>"{service_name}"</b>'
CHOOSE_DATE = "Выберите дату"
CHOOSE_YEAR = "Выберите год"
YEAR_NOT_AVAILABLE = "{lang_year} недоступен для записи"
YEAR_BECOME_NOT_AVAILABLE = "{lang_year} стал недоступен для записи"
CHOOSE_MONTH = "Выберите месяц"
MONTH_NOT_AVAILABLE = "{lang_month_year} недоступен для записи"
MONTH_BECOME_NOT_AVAILABLE = "{lang_month_year} стал недоступен для записи"
CHOOSE_DAY = "Выберите число"
DAY_NOT_AVAILABLE = "{lang_day_month_year} недоступно для записи"
DAY_BECOME_NOT_AVAILABLE = "{lang_day_month_year} стало недоступно для записи"
CHOOSE_TIME = "Выберите время, на которое хотите записаться"
TIME_BECOME_NOT_AVAILABLE = "Время {time} стало недоступно для записи"
CANCELED = "Отменено"
CONFIRM_APPOINTMENT = (
    "Подтвердите запись на прием\n\n"
    "    <i>Услуга</i>: <b>{service_name}</b>\n"
    "    <i>Дата</i>: <b>{lang_day_month_year}</b>\n"
    "    <i>Время</i>: <b>{time}</b>\n\n"
    "Все ли верно?"
)
APPOINTMENT_ERROR = "Возникла ошибка"
TRY_MAKE_APPOINTMENT_AGAIN = "Попробуйте записаться заново"
APPOINTMENT_SAVED = "Запись прошла успешно!"
COME = "Приходите:\n\n{appointment_view}"
NEW_APPOINTMENT_CREATED = "Новая запись на прием!\n\n{appointment_view}"

NO_SCHEDULE = "График работы не задан"
HOW_TO_EDIT_SCHEDULE = (
    'Для изменения графика работы нажмите кнопку <b>"{modify_button}"</b>.\n'
    'Для обнуления графика работы нажмите кнопку <b>"{clear_button}"</b>'
)
SELECT_WORKING_DATES = "Выберите рабочие даты"
SELECT_WORKING_HOURS = "Выберите рабочие часы"
HOW_TO_MODIFY_SCHEDULE = (
    f"Для задания графика работы {SELECT_WORKING_DATES.lower()}, "
    f"{SELECT_WORKING_HOURS.lower()} "
    'и нажмите кнопку <b>"{save_button}"</b>.\n'
    "Если на выбранные даты график работы уже имелся, то рабочие часы будут перезаписаны.\n\n"
    f"Для удаления дат целиком из графика работы {SELECT_WORKING_DATES.lower()} "
    'и нажмите кнопку <b>"{delete_button}"</b>.\n'
    "Для удаления определенных рабочих часов из графика работы "
    f"{SELECT_WORKING_DATES.lower()}, {SELECT_WORKING_HOURS.lower()} "
    'и нажмите кнопку <b>"{delete_button}"</b>'
)
SET_WORKING_DATES = f"<b>{SELECT_WORKING_DATES}:</b>"
SELECTED_WORKING_DATES = "<b>Выбранные рабочие даты:</b>\n{selected_dates_view}"
SET_WORKING_HOURS = f"<b>{SELECT_WORKING_HOURS}:</b>"
SELECTED_WORKING_HOURS = "<b>Выбранные рабочие часы:</b>\n{selected_times_view}"
SCHEDULE_MODIFIED = "График работы изменен"
CLEAR_SCHEDULE_WARNING = (
    "Весь незанятый график работы будет удален.\n"
    "Вы точно хотите обнулить график работы?"
)
SCHEDULE_CLEARED = "График работы обнулен"
