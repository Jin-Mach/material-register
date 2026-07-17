from PySide6.QtCore import QLocale, Qt, QDateTime


_locale = QLocale.system()

def format_number_to_locale(number: float) -> str:
    return _locale.toString(number, "f", 1)

def format_datetime_to_locale(iso_datetime: str) -> str:
    dt = QDateTime.fromString(iso_datetime, Qt.ISODate)
    return _locale.toString(dt, QLocale.FormatType.ShortFormat)