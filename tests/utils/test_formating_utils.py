import pytest
from PySide6.QtCore import QDate, QDateTime, QLocale, QTime

from material_register.utils.formatting_utils import (
    DATE_FORMAT,
    format_date_range_to_locale,
    format_date_to_locale,
    format_date_to_utc,
    format_datetime_to_locale,
    format_number_to_locale,
    format_time_to_locale,
    format_utc_date_to_locale,
)


@pytest.mark.parametrize("number", [1234.5, 0.0, -42.7])
def test_format_number_to_locale(number: float) -> None:
    expected = QLocale().toString(number, "f", 1)
    assert format_number_to_locale(number) == expected


@pytest.mark.parametrize(
    "iso_datetime, expected_datetime",
    [
        ("2026-09-28 15:24:38", QDateTime(2026, 9, 28, 17, 24, 38)),
        ("2026-01-15 12:00:00", QDateTime(2026, 1, 15, 13, 0, 0)),
    ],
)
def test_format_datetime_to_locale(
    iso_datetime: str, expected_datetime: QDateTime
) -> None:
    expected = QLocale().toString(
        expected_datetime,
        QLocale.FormatType.ShortFormat,
    )
    assert format_datetime_to_locale(iso_datetime) == expected


@pytest.mark.parametrize(
    "iso_datetime, expected_date",
    [
        ("2026-09-28 15:24:38", QDate(2026, 9, 28)),
        ("2026-01-15 12:00:00", QDate(2026, 1, 15)),
    ],
)
def test_format_date_to_locale(iso_datetime: str, expected_date: QDate) -> None:
    expected = QLocale().toString(
        expected_date,
        QLocale.FormatType.ShortFormat,
    )
    assert format_date_to_locale(iso_datetime) == expected


@pytest.mark.parametrize(
    "from_date, to_date, expected_from, expected_to",
    [
        (
            "2026-09-27 22:00:00",
            "2026-09-28 15:24:38",
            QDate(2026, 9, 28),
            QDate(2026, 9, 28),
        ),
        (
            "2026-07-05 22:00:00",
            "2026-07-11 15:30:00",
            QDate(2026, 7, 6),
            QDate(2026, 7, 11),
        ),
        (
            "2025-12-31 23:00:00",
            "2026-01-15 12:00:00",
            QDate(2026, 1, 1),
            QDate(2026, 1, 15),
        ),
    ],
)
def test_format_date_range_to_locale(
    from_date: str, to_date: str, expected_from: QDate, expected_to: QDate
) -> None:
    locale = QLocale()
    expected = (
        f"{locale.toString(expected_from, QLocale.FormatType.ShortFormat)} - "
        f"{locale.toString(expected_to, QLocale.FormatType.ShortFormat)}"
    )
    assert format_date_range_to_locale(from_date, to_date) == expected


@pytest.mark.parametrize(
    "iso_datetime, expected_time",
    [
        ("2026-09-28 15:24:38", QTime(17, 24, 38)),
        ("2026-01-15 12:00:00", QTime(13, 0, 0)),
    ],
)
def test_format_time_to_locale(iso_datetime: str, expected_time: QTime) -> None:
    expected = QLocale().toString(
        expected_time,
        QLocale.FormatType.ShortFormat,
    )
    assert format_time_to_locale(iso_datetime) == expected


def test_format_date_to_utc() -> None:
    date = QDate(2026, 9, 28)
    result = format_date_to_utc(date)
    expected = QDateTime(date, QTime(0, 0, 0)).toUTC().toString(DATE_FORMAT)
    assert result == expected


def test_format_date_to_utc_end_of_day() -> None:
    date = QDate(2026, 9, 28)
    result = format_date_to_utc(date, True)
    expected = QDateTime(date, QTime(23, 59, 59)).toUTC().toString(DATE_FORMAT)
    assert result == expected


def test_format_utc_date_to_locale() -> None:
    result = format_utc_date_to_locale("2026-07-05 22:30:00")
    expected = "06.07.2026"
    assert result == expected
