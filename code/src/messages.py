"""Сообщения бота."""

GREETING = "Бот готов к работе!"
NO_USLUGI = "На данный момент никаких услуг нет"
NO_ZAPISI_FOR_ADMIN = "На данный момент никаких записей нет"
NO_ZAPISI_FOR_CLIENT = "У вас пока нет активных записей"
CHOOSE_ACTION = "Выберите действие"
CHOOSE_GIVEN_ACTION = "Выберите действие из предложенных"
MAIN_MENU = "Главное меню"

SET_USLUGA_NAME = "Задайте название услуги"
USLUGA_ALREADY_EXISTS = 'Услуга с названием <b>"{name}"</b> уже существует!'
SET_USLUGA_PRICE = "Задайте цену услуги в рублях\n(например, 300)"
SET_USLUGA_DURATION = (
    "Задайте длительность услуги в минутах (кратно 30)\n(например, 90)"
)
USLUGA_CREATED = 'Услуга <b>"{name}"</b> создана!'

CHOOSE_USLUGA_TO_UPDATE = "Выберите услугу, которую хотите изменить"
CHOOSE_GIVEN_USLUGI = "Выберите услугу из предложенных"
CHOOSE_FIELD_TO_CHANGE = "Выберите, что хотите изменить"
CHOOSE_GIVEN_FIELD_TO_CHANGE = "Выберите из предложенных"

SET_USLUGA_NEW_NAME = "Задайте новое название услуги"
USLUGA_OLD_NAME_AND_NEW_NAME_ARE_SIMILAR = (
    "Новое название ничем не отличается от старого!"
)
USLUGA_NEW_NAME_SETTLED = 'Название "{old_name}" изменено на <b>"{new_name}"</b>'

SET_USLUGA_NEW_PRICE = "Задайте новую цену услуги"
USLUGA_OLD_PRICE_AND_NEW_PRICE_ARE_SIMILAR = "Новая цена не отличается от старой!"
USLUGA_NEW_PRICE_SETTLED = (
    'Цена услуги <b>"{usluga_name}"</b> изменена с {old_price} рублей '
    'на <b>{new_price} рублей</b>'
)

SET_USLUGA_NEW_DURATION = "Задайте новую длительность услуги"
USLUGA_OLD_DURATION_AND_NEW_DURATION_ARE_SIMILAR = (
    "Новая длительность не отличается от старой!"
)
USLUGA_NEW_DURATION_SETTLED = (
    'Длительность услуги <b>"{usluga_name}"</b> изменена с {old_duration} минут '
    'на <b>{new_duration} минут</b>'
)

CHOOSE_USLUGA_TO_DELETE = "Введите порядковый номер услуги, которую хотите удалить"
USLUGA_DELETED = 'Услуга <b>"{name}"</b> удалена!'

CHOOSE_USLUGA_TO_ZAPIS = "Введите порядковый номер услуги, на которую хотите записаться"
CHOOSE_YEAR = "Выберите год"
CHOOSE_GIVEN_YEAR = "Выберите год из предложенных"
CHOOSE_MONTH = "Выберите месяц"
CHOOSE_GIVEN_MONTH = "Выберите месяц из предложенных"
CHOOSE_DAY = "Выберите число"
CHOOSE_GIVEN_DAY = "Выберите число из предложенных"
CHOOSE_TIME = "Выберите время, на которое хотите записаться"
CHOOSE_GIVEN_TIME = "Выберите время из предложенных"
ZAPIS_SAVED = "Запись прошла успешно!\nПриходите:\n\n{zapis_view}"
NEW_ZAPIS_CREATED = "Новая запись на прием!\n\n{zapis_view}"
