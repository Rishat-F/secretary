class DateTimeBecomeNotAvailable(Exception):
    """Дата и время стало недоступно."""


class YearBecomeNotAvailable(DateTimeBecomeNotAvailable):
    """Год стал недоступен."""


class MonthBecomeNotAvailable(DateTimeBecomeNotAvailable):
    """Месяц года стал недоступен."""


class DayBecomeNotAvailable(DateTimeBecomeNotAvailable):
    """День года и месяца стал недоступен."""


class TimeBecomeNotAvailable(DateTimeBecomeNotAvailable):
    """Время года, месяца и дня стало недоступно."""
