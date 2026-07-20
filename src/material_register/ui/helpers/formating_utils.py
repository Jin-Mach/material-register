from PySide6.QtCore import QLocale, Qt, QDateTime


DATE_FORMAT = "yyyy-MM-dd HH:mm:ss"

_locale = QLocale()

def format_number_to_locale(number: float) -> str:
    return _locale.toString(number, "f", 1)

def format_datetime_to_locale(iso_datetime: str) -> str:
    date_time = QDateTime.fromString(iso_datetime, DATE_FORMAT)
    date_time.setTimeSpec(Qt.TimeSpec.UTC)
    date_time = date_time.toLocalTime()
    return _locale.toString(date_time, QLocale.FormatType.ShortFormat)