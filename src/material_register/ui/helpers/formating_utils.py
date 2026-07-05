from PySide6.QtCore import QLocale


def format_number_to_locale(number: float) -> str:
    return QLocale().toString(number, "f", 1)