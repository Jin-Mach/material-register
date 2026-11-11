import pytest

from material_register.db.config.advanced_search_queries_constants import (
    ADVANCED_SEARCH_AMOUNT_EXPRESSION,
    ADVANCED_SEARCH_COLUMNS,
    HAVING_CLAUSE,
    WHERE_CLAUSE,
)
from material_register.domain.advanced_search_dataclass import (
    AdvancedSearchDataclass,
    MaterialFiltersDataclass,
    MaterialSearchDataclass,
)
from material_register.services.advanced_filter_builder import AdvancedFilterBuilder
from material_register.ui.config.ui_constants import PAYMENT_CASH, TRANSFER_IN


def _empty_material_filters() -> MaterialFiltersDataclass:
    return MaterialFiltersDataclass(operator="AND", filters=[])


MATERIAL_CATEGORY_CONDITION = "material_category.id = ?"
MATERIAL_COMMODITY_CONDITION = "material_commodity.id = ?"
MATERIAL_AMOUNT_CONDITION = "SUM(material_item.unit_count) < ?"
MATERIAL_UNIT_PRICE_CONDITION = "price_item.price_per_unit = ?"
MATERIAL_TOTAL_PRICE_CONDITION = (
    "SUM(material_item.unit_count * material_item.price_per_unit) > ?"
)


def test_create_advanced_filter_without_filters() -> None:
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        [], _empty_material_filters()
    )
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
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters, _empty_material_filters()
    )
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
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters, _empty_material_filters()
    )
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
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters, _empty_material_filters()
    )
    assert where == "WHERE trans.created_at BETWEEN ? AND ?"
    assert having == ""
    assert params == ["2026-10-01 22:00:00", "2026-10-20 21:59:59"]


@pytest.mark.parametrize(
    ("column", "query", "value"),
    [
        ("transaction_id", "= ?", 81),
        ("transaction_is_invoiced", "= ?", 0),
        ("transaction_notes", "LIKE ?", "%transaction note%"),
        ("customer_company_name", "LIKE ?", "company%"),
        ("customer_first_name", "LIKE ?", "jan%"),
        ("customer_last_name", "LIKE ?", "%novak"),
        ("customer_document", "LIKE ?", "%123%"),
        ("customer_address", "LIKE ?", "%town%"),
        ("customer_active", "= ?", 1),
        ("customer_notes", "LIKE ?", "%customer note%"),
    ],
)
def test_create_where_query_with_other_filter_fields(
    column: str, query: str, value: str | int
) -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS[column],
            query=query,
            value=value,
        )
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters, _empty_material_filters()
    )
    assert where == f"WHERE {ADVANCED_SEARCH_COLUMNS[column]} {query}"
    assert having == ""
    assert params == [value]


def test_create_having_query_with_total_filter() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["total"],
            query="< ?",
            value=555.0,
        )
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters, _empty_material_filters()
    )
    assert where == ""
    assert having == "HAVING trans.type = 'IN' AND total < ?"
    assert params == [555.0]


def test_create_amount_having_query_with_total_filter() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["total"],
            query="< ?",
            value=555.0,
        )
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters,
        _empty_material_filters(),
        amount_having=True,
    )
    assert where == ""
    assert having.startswith("GROUP BY trans.id HAVING")
    assert ADVANCED_SEARCH_AMOUNT_EXPRESSION.strip() in having
    assert params == [555.0]


def test_create_amount_having_query_with_multiple_filters() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["total"],
            query="> ?",
            value=100.0,
        ),
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["transaction_id"],
            query="< ?",
            value=50,
        ),
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters,
        _empty_material_filters(),
        amount_having=True,
    )
    assert where == ""
    assert having.startswith("GROUP BY trans.id HAVING")
    assert ADVANCED_SEARCH_AMOUNT_EXPRESSION.strip() in having
    assert "AND trans.id < ?" in having
    assert params == [100.0, 50]


def test_create_amount_having_query_with_where_and_having_filters() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["transaction_type"],
            query="= ?",
            value=TRANSFER_IN,
        ),
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["total"],
            query="> ?",
            value=100.0,
        ),
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters,
        _empty_material_filters(),
        amount_having=True,
    )
    assert where == "WHERE trans.type = ?"
    assert having.startswith("GROUP BY trans.id HAVING")
    assert ADVANCED_SEARCH_AMOUNT_EXPRESSION.strip() in having
    assert params == [TRANSFER_IN, 100.0]


def test_create_material_having_query_with_total_filter() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["total"],
            query="> ?",
            value=100.0,
        )
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters,
        _empty_material_filters(),
        material_having=True,
    )
    assert where == ""
    assert having.startswith("GROUP BY trans.id HAVING")
    assert "trans.type = 'IN'" in having
    assert ADVANCED_SEARCH_AMOUNT_EXPRESSION.strip() in having
    assert "> ?" in having
    assert params == [100.0]


def test_create_material_having_query_with_multiple_filters() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["total"],
            query="> ?",
            value=100.0,
        ),
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["transaction_id"],
            query="< ?",
            value=50,
        ),
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters,
        _empty_material_filters(),
        material_having=True,
    )
    assert where == ""
    assert having.startswith("GROUP BY trans.id HAVING")
    assert "trans.type = 'IN'" in having
    assert ADVANCED_SEARCH_AMOUNT_EXPRESSION.strip() in having
    assert "AND trans.id < ?" in having
    assert params == [100.0, 50]


def test_create_material_having_query_with_where_and_having_filters() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["transaction_type"],
            query="= ?",
            value=TRANSFER_IN,
        ),
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["total"],
            query="> ?",
            value=100.0,
        ),
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters,
        _empty_material_filters(),
        material_having=True,
    )
    assert where == "WHERE trans.type = ?"
    assert having.startswith("GROUP BY trans.id HAVING")
    assert "trans.type = 'IN'" in having
    assert ADVANCED_SEARCH_AMOUNT_EXPRESSION.strip() in having
    assert params == [TRANSFER_IN, 100.0]


@pytest.mark.parametrize(
    ("query", "expected"),
    [
        ("IS NULL", "cust.company IS NULL"),
        ("IS NOT NULL", "cust.company IS NOT NULL"),
    ],
    ids=["company", "individual"],
)
def test_create_where_query_with_customer_subject_type(
    query: str, expected: str
) -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["customer_subject_type"],
            query=query,
            value="",
        )
    ]
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters, _empty_material_filters()
    )
    assert where == f"WHERE {expected}"
    assert having == ""
    assert params == []


@pytest.mark.parametrize(
    ("material_filter", "expected_conditions", "expected_params"),
    [
        (
            MaterialSearchDataclass(category_id=2),
            [MATERIAL_CATEGORY_CONDITION],
            [2],
        ),
        (
            MaterialSearchDataclass(commodity_id=4),
            [MATERIAL_COMMODITY_CONDITION],
            [4],
        ),
        (
            MaterialSearchDataclass(category_id=2, commodity_id=4),
            [MATERIAL_CATEGORY_CONDITION, MATERIAL_COMMODITY_CONDITION],
            [2, 4],
        ),
        (
            MaterialSearchDataclass(
                commodity_id=4, amount_operator="<", amount_value=5.0
            ),
            [MATERIAL_COMMODITY_CONDITION, MATERIAL_AMOUNT_CONDITION],
            [4, 5.0],
        ),
        (
            MaterialSearchDataclass(
                category_id=2,
                commodity_id=4,
                amount_operator="<",
                amount_value=5.0,
            ),
            [
                MATERIAL_CATEGORY_CONDITION,
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_AMOUNT_CONDITION,
            ],
            [2, 4, 5.0],
        ),
        (
            MaterialSearchDataclass(
                commodity_id=4,
                price_per_unit_operator="=",
                price_per_unit_value=20.0,
            ),
            [MATERIAL_COMMODITY_CONDITION, MATERIAL_UNIT_PRICE_CONDITION],
            [4, 20.0],
        ),
        (
            MaterialSearchDataclass(
                category_id=2,
                commodity_id=4,
                price_per_unit_operator="=",
                price_per_unit_value=20.0,
            ),
            [
                MATERIAL_CATEGORY_CONDITION,
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_UNIT_PRICE_CONDITION,
            ],
            [2, 4, 20.0],
        ),
        (
            MaterialSearchDataclass(
                commodity_id=4,
                total_price_operator=">",
                total_price_value=30.0,
            ),
            [MATERIAL_COMMODITY_CONDITION, MATERIAL_TOTAL_PRICE_CONDITION],
            [4, 30.0],
        ),
        (
            MaterialSearchDataclass(
                category_id=2,
                commodity_id=4,
                total_price_operator=">",
                total_price_value=30.0,
            ),
            [
                MATERIAL_CATEGORY_CONDITION,
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_TOTAL_PRICE_CONDITION,
            ],
            [2, 4, 30.0],
        ),
        (
            MaterialSearchDataclass(
                commodity_id=4,
                amount_operator="<",
                amount_value=5.0,
                price_per_unit_operator="=",
                price_per_unit_value=20.0,
            ),
            [
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_AMOUNT_CONDITION,
                MATERIAL_UNIT_PRICE_CONDITION,
            ],
            [4, 5.0, 20.0],
        ),
        (
            MaterialSearchDataclass(
                category_id=2,
                commodity_id=4,
                amount_operator="<",
                amount_value=5.0,
                price_per_unit_operator="=",
                price_per_unit_value=20.0,
            ),
            [
                MATERIAL_CATEGORY_CONDITION,
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_AMOUNT_CONDITION,
                MATERIAL_UNIT_PRICE_CONDITION,
            ],
            [2, 4, 5.0, 20.0],
        ),
        (
            MaterialSearchDataclass(
                commodity_id=4,
                amount_operator="<",
                amount_value=5.0,
                total_price_operator=">",
                total_price_value=30.0,
            ),
            [
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_AMOUNT_CONDITION,
                MATERIAL_TOTAL_PRICE_CONDITION,
            ],
            [4, 5.0, 30.0],
        ),
        (
            MaterialSearchDataclass(
                category_id=2,
                commodity_id=4,
                amount_operator="<",
                amount_value=5.0,
                total_price_operator=">",
                total_price_value=30.0,
            ),
            [
                MATERIAL_CATEGORY_CONDITION,
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_AMOUNT_CONDITION,
                MATERIAL_TOTAL_PRICE_CONDITION,
            ],
            [2, 4, 5.0, 30.0],
        ),
        (
            MaterialSearchDataclass(
                commodity_id=4,
                price_per_unit_operator="=",
                price_per_unit_value=20.0,
                total_price_operator=">",
                total_price_value=30.0,
            ),
            [
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_UNIT_PRICE_CONDITION,
                MATERIAL_TOTAL_PRICE_CONDITION,
            ],
            [4, 20.0, 30.0],
        ),
        (
            MaterialSearchDataclass(
                category_id=2,
                commodity_id=4,
                price_per_unit_operator="=",
                price_per_unit_value=20.0,
                total_price_operator=">",
                total_price_value=30.0,
            ),
            [
                MATERIAL_CATEGORY_CONDITION,
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_UNIT_PRICE_CONDITION,
                MATERIAL_TOTAL_PRICE_CONDITION,
            ],
            [2, 4, 20.0, 30.0],
        ),
        (
            MaterialSearchDataclass(
                commodity_id=4,
                amount_operator="<",
                amount_value=5.0,
                price_per_unit_operator="=",
                price_per_unit_value=20.0,
                total_price_operator=">",
                total_price_value=30.0,
            ),
            [
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_AMOUNT_CONDITION,
                MATERIAL_UNIT_PRICE_CONDITION,
                MATERIAL_TOTAL_PRICE_CONDITION,
            ],
            [4, 5.0, 20.0, 30.0],
        ),
        (
            MaterialSearchDataclass(
                category_id=2,
                commodity_id=4,
                amount_operator="<",
                amount_value=5.0,
                price_per_unit_operator="=",
                price_per_unit_value=20.0,
                total_price_operator=">",
                total_price_value=30.0,
            ),
            [
                MATERIAL_CATEGORY_CONDITION,
                MATERIAL_COMMODITY_CONDITION,
                MATERIAL_AMOUNT_CONDITION,
                MATERIAL_UNIT_PRICE_CONDITION,
                MATERIAL_TOTAL_PRICE_CONDITION,
            ],
            [2, 4, 5.0, 20.0, 30.0],
        ),
    ],
)
def test_create_material_filter_combinations(
    material_filter: MaterialSearchDataclass,
    expected_conditions: list[str],
    expected_params: list[int | float],
) -> None:
    material_filters = MaterialFiltersDataclass(
        operator="AND",
        filters=[material_filter],
    )
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        [], material_filters
    )
    for expected_condition in expected_conditions:
        assert expected_condition in where
    assert where.count("?") == len(expected_params)
    assert "GROUP BY material_item.transaction_id, material_commodity.id" in where
    assert having == ""
    assert params == expected_params


@pytest.mark.parametrize("operator", ["AND", "OR"])
def test_create_multiple_material_filters_with_operator(operator: str) -> None:
    material_filters = MaterialFiltersDataclass(
        operator=operator,
        filters=[
            MaterialSearchDataclass(category_id=2),
            MaterialSearchDataclass(
                commodity_id=4,
                amount_operator="<",
                amount_value=5.0,
            ),
        ],
    )

    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        [], material_filters
    )
    assert where.startswith("WHERE (")
    assert where.count("EXISTS (") == 2
    assert f") {operator}" in where
    assert "material_category.id = ?" in where
    assert "material_commodity.id = ?" in where
    assert "SUM(material_item.unit_count) < ?" in where
    assert where.endswith("))")
    assert having == ""
    assert params == [2, 4, 5.0]


def test_create_material_filter_with_regular_where_filter() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["transaction_type"],
            query="= ?",
            value=TRANSFER_IN,
        )
    ]
    material_filters = MaterialFiltersDataclass(
        operator="AND",
        filters=[MaterialSearchDataclass(category_id=2, commodity_id=4)],
    )
    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters, material_filters
    )
    assert where.startswith("WHERE trans.type = ? AND (")
    assert "material_category.id = ?" in where
    assert "material_commodity.id = ?" in where
    assert having == ""
    assert params == [TRANSFER_IN, 2, 4]


def test_create_material_filter_with_regular_where_and_having_filters() -> None:
    filters = [
        AdvancedSearchDataclass(
            clause=WHERE_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["transaction_type"],
            query="= ?",
            value=TRANSFER_IN,
        ),
        AdvancedSearchDataclass(
            clause=HAVING_CLAUSE,
            column_name=ADVANCED_SEARCH_COLUMNS["total"],
            query="< ?",
            value=1000.0,
        ),
    ]
    material_filters = MaterialFiltersDataclass(
        operator="AND",
        filters=[
            MaterialSearchDataclass(
                category_id=2,
                commodity_id=4,
                amount_operator="<",
                amount_value=5.0,
            )
        ],
    )

    where, having, params = AdvancedFilterBuilder.create_advanced_filter(
        filters, material_filters
    )
    assert where.startswith("WHERE trans.type = ? AND (")
    assert "material_category.id = ?" in where
    assert "material_commodity.id = ?" in where
    assert "SUM(material_item.unit_count) < ?" in where
    assert having == "HAVING trans.type = 'IN' AND total < ?"
    assert params == [TRANSFER_IN, 2, 4, 5.0, 1000.0]
