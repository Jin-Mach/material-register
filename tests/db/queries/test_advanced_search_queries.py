import uuid

import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.advanced_search_queries_constants import (
    ADVANCED_SEARCH_AMOUNT_EXPRESSION,
)
from material_register.db.queries.advanced_search_queries import (
    AdvancedSearchQueries,
)


@pytest.fixture
def connection() -> QSqlDatabase:
    connection_name = f"test_advanced_search_queries_{uuid.uuid4().hex}"
    conn = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


@pytest.fixture
def schema(connection: QSqlDatabase) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            company TEXT,
            first_name TEXT,
            last_name TEXT,
            document_number TEXT,
            address TEXT,
            company_normalized TEXT,
            first_name_normalized TEXT,
            last_name_normalized TEXT,
            address_normalized TEXT
        )
    """)
    query.exec("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            type TEXT,
            customer_id INTEGER,
            created_at TEXT,
            payment_type TEXT,
            is_invoiced INTEGER,
            notes TEXT
        )
    """)
    query.exec("""
        CREATE TABLE transaction_items (
            id INTEGER PRIMARY KEY,
            transaction_id INTEGER,
            commodity_id INTEGER,
            unit_count REAL,
            price_per_unit REAL
        )
    """)
    query.exec("""
        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY,
            name TEXT,
            unit TEXT,
            category_id INTEGER
        )
    """)
    query.exec("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)


@pytest.fixture
def sample_data(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO customers (
            id, company, first_name, last_name, document_number, address
        )
        VALUES
            (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars'),
            (2, NULL, 'John', 'Doe', 'ID456', 'Venus')
    """)
    query.exec("""
        INSERT INTO categories (id, name)
        VALUES (1, 'Metals')
    """)
    query.exec("""
        INSERT INTO commodities (id, name, unit, category_id)
        VALUES (1, 'Steel', 'kg', 1)
    """)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at,
            payment_type, is_invoiced, notes
        )
        VALUES
            (1, 'IN', 1, '2026-10-18 10:00:00',
             'TRANSFER', 0, 'First transaction'),
            (2, 'OUT', 1, '2026-10-19 10:00:00',
             NULL, 1, 'Second transaction'),
            (3, 'IN', 2, '2026-10-20 10:00:00',
             'CASH', 0, 'Third transaction')
    """)
    query.exec("""
        INSERT INTO transaction_items (
            id, transaction_id, commodity_id, unit_count, price_per_unit
        )
        VALUES
            (1, 1, 1, 10, 20),
            (2, 2, 1, 10, 20),
            (3, 3, 1, 5, 30)
    """)


def test_load_transactions(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    success, results = AdvancedSearchQueries.load_transactions(connection, "", "", [])
    assert success is True
    assert len(results) == 3
    transaction_ids = []
    for transaction in results:
        transaction_ids.append(transaction.transaction_id)
    assert transaction_ids == [3, 2, 1]
    transaction_in = None
    transaction_out = None
    for transaction in results:
        if transaction.transaction_id == 1:
            transaction_in = transaction
        elif transaction.transaction_id == 2:
            transaction_out = transaction
    assert transaction_in.transaction_type == "IN"
    assert transaction_in.total == 200.0
    assert transaction_in.suffix is None
    assert transaction_in.customer_name == "Fake company"
    assert transaction_out.transaction_type == "OUT"
    assert transaction_out.total == 10.0
    assert transaction_out.suffix == "kg"
    assert transaction_out.is_invoiced is True


def test_load_transactions_where_filter(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    where = "WHERE trans.type = ?"
    params = ["IN"]
    success, results = AdvancedSearchQueries.load_transactions(
        connection, where, "", params
    )
    assert success is True
    assert len(results) == 2
    transaction_ids = []
    for transaction in results:
        transaction_ids.append(transaction.transaction_id)
    assert transaction_ids == [3, 1]


def test_load_transactions_having_filter(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    having = "HAVING total = ?"
    params = [200.0]
    success, results = AdvancedSearchQueries.load_transactions(
        connection, "", having, params
    )
    assert success is True
    assert len(results) == 1
    assert results[0].transaction_id == 1
    assert results[0].total == 200.0


def test_load_transactions_where_and_having_filters(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    where = "WHERE trans.type = ?"
    having = "HAVING total > ?"
    params = ["IN", 100.0]
    success, results = AdvancedSearchQueries.load_transactions(
        connection, where, having, params
    )
    assert success is True
    assert len(results) == 2
    transaction_ids = []
    for transaction in results:
        transaction_ids.append(transaction.transaction_id)
    assert transaction_ids == [3, 1]


def test_load_transactions_query_error(
    connection: QSqlDatabase,
) -> None:
    success, results = AdvancedSearchQueries.load_transactions(connection, "", "", [])
    assert success is False
    assert results == []


def test_get_total_amount(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    success, total_amount = AdvancedSearchQueries.get_total_amount(
        connection, "", "", []
    )
    assert success is True
    assert total_amount == 350.0


def test_get_total_amount_where_filter(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    where = "WHERE trans.id = ?"
    params = [1]
    success, total_amount = AdvancedSearchQueries.get_total_amount(
        connection, where, "", params
    )
    assert success is True
    assert total_amount == 200.0


def test_get_total_amount_having_filter(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    having = "GROUP BY trans.id HAVING " + ADVANCED_SEARCH_AMOUNT_EXPRESSION + " > ?"
    params = [175.0]
    success, total_amount = AdvancedSearchQueries.get_total_amount(
        connection, "", having, params
    )
    assert success is True
    assert total_amount == 200.0


def test_get_total_amount_where_and_having_filters(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    where = "WHERE trans.type = ?"
    having = "GROUP BY trans.id HAVING " + ADVANCED_SEARCH_AMOUNT_EXPRESSION + " > ?"
    params = ["IN", 175.0]
    success, total_amount = AdvancedSearchQueries.get_total_amount(
        connection, where, having, params
    )
    assert success is True
    assert total_amount == 200.0


def test_get_total_amount_multiple_items(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transaction_items (
            id, transaction_id, commodity_id, unit_count, price_per_unit
        )
        VALUES
            (4, 1, 1, 2, 15),
            (5, 1, 1, 3, 10),
            (6, 1, 1, 4, 5)
    """)
    success, total_amount = AdvancedSearchQueries.get_total_amount(
        connection, "", "", []
    )
    assert success is True
    assert total_amount == 430.0


def test_get_total_amount_no_matching_transactions(
    connection: QSqlDatabase,
    sample_data,
) -> None:
    where = "WHERE trans.type = ?"
    params = ["UNKNOWN"]
    success, total_amount = AdvancedSearchQueries.get_total_amount(
        connection, where, "", params
    )
    assert success is True
    assert total_amount == 0.0


def test_get_total_amount_query_error(
    connection: QSqlDatabase,
) -> None:
    success, total_amount = AdvancedSearchQueries.get_total_amount(
        connection, "", "", []
    )
    assert success is False
    assert total_amount == 0.0
