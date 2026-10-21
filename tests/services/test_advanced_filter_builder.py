import pytest

from material_register.db.config.advanced_search_queries_constants import (
    ADVANCED_SEARCH_COLUMNS,
    HAVING_CLAUSE,
    WHERE_CLAUSE,
)
from material_register.domain.adavanced_search_dataclass import AdvancedSearchDataclass
from material_register.services.advanced_filter_builder import AdvancedFilterBuilder
from material_register.ui.config.ui_constants import PAYMENT_CASH, TRANSFER_IN


def test_create_advanced_filter_without_filters() -> None:
    where, having, params = AdvancedFilterBuilder.create_advanced_filter([])
    assert where == ""
    assert having == ""
    assert params == []


@pytest.mark.parametrize(
    ("column_name", "value", "expected"),
    [
        (ADVANCED_SEARCH_COLUMNS["transaction_type"], TRANSFER_IN, "trans.type = ?"),
        (
            ADVANCED_SEARCH_COLUMNS["transaction_payment_type"],
            PAYMENT_CASH,
            "trans.payment_type = ?",
        ),
    ],
)
def test_create_where_query_with_single_filter(
    column_name: str,
    value: str,
    expected: str,
) -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=column_name,
            query="= ?",
            value=value,
        )
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(filters)
    assert where == f"WHERE {expected}"
    assert having == ""
    assert params == [value]


def test_create_where_query_with_multiple_filters() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["transaction_type"],
            query="= ?",
            value=TRANSFER_IN,
        ),
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["transaction_payment_type"],
            query="= ?",
            value=PAYMENT_CASH,
        ),
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(filters)
    assert where == "WHERE trans.type = ? AND trans.payment_type = ?"
    assert having == ""
    assert params == [TRANSFER_IN, PAYMENT_CASH]


def test_create_where_query_with_date_range() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["transaction_created_at"],
            query="BETWEEN ? AND ?",
            value=("2026-10-01 22:00:00", "2026-10-20 21:59:59"),
        )
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(filters)
    assert where == "WHERE trans.created_at BETWEEN ? AND ?"
    assert having == ""
    assert params == ["2026-10-01 22:00:00", "2026-10-20 21:59:59"]


def test_create_having_query_with_total_filter() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["total"],
            query="< ?",
            value=555.0,
        )
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(filters)
    assert where == ""
    assert having == "HAVING trans.type = 'IN' AND total < ?"
    assert params == [555.0]
