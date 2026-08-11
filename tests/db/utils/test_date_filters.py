from datetime import datetime

import pytest

from material_register.utils.date_filters import get_filter_range


@pytest.mark.parametrize(
    "key, expected_start",
    [
        ("today", "2026-07-11 00:00:00"),
        ("week", "2026-07-06 00:00:00"),
        ("month", "2026-07-01 00:00:00"),
        ("year", "2026-01-01 00:00:00"),
    ],
)
def test_filter_range_start_dates(monkeypatch, key: str, expected_start: str) -> None:
    fixed_now = datetime(2026, 7, 11, 15, 30, 45)
    monkeypatch.setattr(
        "material_register.utils.date_filters._now",
        lambda: fixed_now,
    )
    start, end = get_filter_range(key)
    assert start == expected_start
    assert end == "2026-07-11 15:30:45"

def test_week_filter_is_monday_to_current_day(monkeypatch) -> None:
    fixed_now = datetime(2026, 7, 15, 10, 0, 0)
    monkeypatch.setattr(
        "material_register.utils.date_filters._now",
        lambda: fixed_now,
    )
    start, end = get_filter_range("week")
    assert start == "2026-07-13 00:00:00"
    assert end == "2026-07-15 10:00:00"

@pytest.mark.parametrize(
    "fixed_date, expected_start",
    [
        (datetime(2026, 1, 31, 12, 0), "2026-01-01 00:00:00"),
        (datetime(2026, 2, 28, 12, 0), "2026-02-01 00:00:00"),
        (datetime(2026, 3, 31, 12, 0), "2026-03-01 00:00:00"),
        (datetime(2026, 12, 31, 12, 0), "2026-12-01 00:00:00"),
    ],
)
def test_month_filter_starts_first_day(monkeypatch, fixed_date: datetime, expected_start: str) -> None:
    monkeypatch.setattr(
        "material_register.utils.date_filters._now",
        lambda: fixed_date,
    )
    start, end = get_filter_range("month")
    assert start == expected_start
    assert end == fixed_date.strftime("%Y-%m-%d %H:%M:%S")

@pytest.mark.parametrize(
    "fixed_date",
    [
        datetime(2026, 1, 1, 0, 0),
        datetime(2026, 6, 15, 12, 0),
        datetime(2026, 12, 31, 23, 59),
    ],
)
def test_year_filter_starts_first_january(monkeypatch, fixed_date: datetime) -> None:
    monkeypatch.setattr(
        "material_register.utils.date_filters._now",
        lambda: fixed_date,
    )
    start, end = get_filter_range("year")
    assert start == "2026-01-01 00:00:00"
    assert end == fixed_date.strftime("%Y-%m-%d %H:%M:%S")

def test_invalid_filter_returns_none(monkeypatch) -> None:
    fixed_now = datetime(2026, 7, 11, 15, 30, 45)
    monkeypatch.setattr(
        "material_register.utils.date_filters._now",
        lambda: fixed_now,
    )
    result = get_filter_range("invalid")
    assert result is None