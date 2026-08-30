from PySide6.QtCore import QDateTime, QLocale, Qt

DATE_FORMAT = "yyyy-MM-dd HH:mm:ss"

_locale = QLocale()


def format_number_to_locale(number: float) -> str:
    return _locale.toString(float(number), "f", 1)


def format_datetime_to_locale(iso_datetime: str) -> str:
    date_time = QDateTime.fromString(iso_datetime, DATE_FORMAT)
    date_time.setTimeSpec(Qt.TimeSpec.UTC)
    date_time = date_time.toLocalTime()
    return _locale.toString(date_time, QLocale.FormatType.ShortFormat)


def format_date_to_locale(iso_datetime: str) -> str:
    date_time = QDateTime.fromString(iso_datetime, DATE_FORMAT)
    return _locale.toString(date_time.date(), QLocale.FormatType.ShortFormat)


def format_date_range_to_locale(from_date: str, to_date: str) -> str:
    from_formatted = format_date_to_locale(from_date)
    to_formatted = format_date_to_locale(to_date)
    return f"{from_formatted} - {to_formatted}"


def format_time_to_locale(iso_datetime: str) -> str:
    date_time = QDateTime.fromString(iso_datetime, DATE_FORMAT)
    date_time.setTimeSpec(Qt.TimeSpec.UTC)
    date_time = date_time.toLocalTime()
    return _locale.toString(date_time.time(), QLocale.FormatType.ShortFormat)
