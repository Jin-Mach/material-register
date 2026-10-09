import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.search_queries import SearchQueries


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "search_test")
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
            address TEXT
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
            unit TEXT
        )
    """)


def test_load_transactions(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'kg')")
    query.exec("""
        INSERT INTO customers
        VALUES (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars')
    """)
    query.exec("""
        INSERT INTO transactions
            (id, type, customer_id, created_at, payment_type, is_invoiced, notes)
        VALUES
            (1, 'IN', 1, '2020-01-01 10:00:00', 'TRANSFER', 0, NULL),
            (2, 'OUT', 1, '2020-01-02 10:00:00', NULL, 1, NULL)
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES
            (1, 1, 1, 10, 20),
            (2, 2, 1, 10, 20)
    """)
    success, results = SearchQueries.load_transactions(connection)
    assert success is True
    assert len(results) == 2
    transaction_in = None
    transaction_out = None
    for transaction in results:
        if transaction.transaction_type == "IN":
            transaction_in = transaction
        elif transaction.transaction_type == "OUT":
            transaction_out = transaction
    assert transaction_in.total == 200.0
    assert transaction_in.suffix is None
    assert transaction_out.total == 10.0
    assert transaction_out.suffix == "kg"
    assert transaction_out.is_invoiced is True


def test_load_transactions_includes_older_transactions(
    connection: QSqlDatabase, schema
) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'kg')")
    query.exec("""
        INSERT INTO customers
        VALUES (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars')
    """)
    query.exec("""
        INSERT INTO transactions
            (id, type, customer_id, created_at, payment_type, is_invoiced)
        VALUES
            (1, 'IN', 1, '2020-01-01 10:00:00', 'TRANSFER', 0)
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES (1, 1, 1, 10, 20)
    """)
    success, results = SearchQueries.load_transactions(connection)
    assert success is True
    assert len(results) == 1
    assert results[0].transaction_id == 1


def test_load_transactions_query_error(connection: QSqlDatabase) -> None:
    success, results = SearchQueries.load_transactions(connection)
    assert success is False
    assert results == []
