import pytest

from material_register.db.config.search_queries_constants import (
    SEARCH_PERIOD_QUERY,
    SEARCH_VALUE_QUERY,
)
from material_register.services.filter_builder import FilterBuilder


@pytest.mark.parametrize(
    "period_key, value, expected",
    [
        (None, "John Doe", f"WHERE {SEARCH_VALUE_QUERY}"),
        ("today", "", f"WHERE {SEARCH_PERIOD_QUERY}"),
        ("week", "", f"WHERE {SEARCH_PERIOD_QUERY}"),
        ("month", "", f"WHERE {SEARCH_PERIOD_QUERY}"),
        ("year", "", f"WHERE {SEARCH_PERIOD_QUERY}"),
        ("today", "John Doe", f"WHERE {SEARCH_PERIOD_QUERY} AND {SEARCH_VALUE_QUERY}"),
        ("week", "John Doe", f"WHERE {SEARCH_PERIOD_QUERY} AND {SEARCH_VALUE_QUERY}"),
        ("month", "John Doe", f"WHERE {SEARCH_PERIOD_QUERY} AND {SEARCH_VALUE_QUERY}"),
        ("year", "John Doe", f"WHERE {SEARCH_PERIOD_QUERY} AND {SEARCH_VALUE_QUERY}"),
    ],
    ids=[
        "text-only",
        "today-only",
        "week-only",
        "month-only",
        "year-only",
        "today-and-text",
        "week-and-text",
        "month-and-text",
        "year-and-text",
    ],
)
def test_create_basic_filter(period_key: str | None, value: str, expected: str) -> None:
    query, _ = FilterBuilder.create_basic_filter(period_key, value)
    assert query == expected


def test_create_basic_filter_without_filters() -> None:
    where, params = FilterBuilder.create_basic_filter(None, "")
    assert where == ""
    assert params == []
