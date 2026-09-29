from PySide6.QtCore import QDate, QDateTime, QLocale, QTimeZone

DATE_FORMAT = "yyyy-MM-dd HH:mm:ss"

_locale = QLocale()


def format_number_to_locale(number: float) -> str:
    return _locale.toString(float(number), "f", 1)


def format_datetime_to_locale(iso_datetime: str) -> str:
    date_time = QDateTime.fromString(iso_datetime, DATE_FORMAT)
    date_time.setTimeZone(QTimeZone.utc())
    date_time = date_time.toLocalTime()
    return _locale.toString(date_time, QLocale.FormatType.ShortFormat)


def format_date_to_locale(iso_datetime: str) -> str:
    date_time = QDateTime.fromString(iso_datetime, DATE_FORMAT)
    return _locale.toString(date_time.date(), QLocale.FormatType.ShortFormat)


def format_date_range_to_locale(from_date: str, to_date: str) -> str:
    from_date_time = QDateTime.fromString(from_date, DATE_FORMAT)
    from_date_time.setTimeZone(QTimeZone.utc())
    from_date_time = from_date_time.toLocalTime()
    to_date_time = QDateTime.fromString(to_date, DATE_FORMAT)
    to_date_time.setTimeZone(QTimeZone.utc())
    to_date_time = to_date_time.toLocalTime()
    from_formatted = _locale.toString(
        from_date_time.date(), QLocale.FormatType.ShortFormat
    )
    to_formatted = _locale.toString(to_date_time.date(), QLocale.FormatType.ShortFormat)
    return f"{from_formatted} - {to_formatted}"


def format_time_to_locale(iso_datetime: str) -> str:
    date_time = QDateTime.fromString(iso_datetime, DATE_FORMAT)
    date_time.setTimeZone(QTimeZone.utc())
    date_time = date_time.toLocalTime()
    return _locale.toString(date_time.time(), QLocale.FormatType.ShortFormat)


def format_current_datetime_to_locale() -> str:
    return _locale.toString(
        QDateTime.currentDateTime(),
        QLocale.FormatType.ShortFormat,
    )


def format_date_to_utc(date: QDate, end_of_day: bool = False) -> str:
    if end_of_day:
        time = "23:59:59"
    else:
        time = "00:00:00"
    date_time = QDateTime.fromString(
        f"{date.toString('yyyy-MM-dd')} {time}",
        DATE_FORMAT,
    )
    date_time.setTimeZone(QTimeZone.systemTimeZone())
    date_time = date_time.toUTC()
    return date_time.toString(DATE_FORMAT)


def format_utc_date_to_locale(iso_datetime: str) -> str:
    date_time = QDateTime.fromString(iso_datetime, DATE_FORMAT)
    date_time.setTimeZone(QTimeZone.utc())
    date_time = date_time.toLocalTime()
    return _locale.toString(date_time.date(), QLocale.FormatType.ShortFormat)
