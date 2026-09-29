from datetime import UTC, datetime

import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.transactions_load_queries import (
    TransactionsLoadQueries,
)


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "load_test")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


@pytest.fixture
def schema(connection) -> None:
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
            unit TEXT
        )
    """)


def get_timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S")


def test_load_transaction_in(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'kg')")
    query.exec(
        "INSERT INTO customers VALUES (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars', NULL, NULL, NULL, NULL)"
    )
    query.prepare("""
        INSERT INTO transactions (
        id, type, customer_id, created_at, payment_type, is_invoiced
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """)
    query.addBindValue(1)
    query.addBindValue("IN")
    query.addBindValue(1)
    query.addBindValue(get_timestamp())
    query.addBindValue("TRANSFER")
    query.addBindValue(0)
    query.exec()
    query.exec("INSERT INTO transaction_items VALUES (1, 1, 1, 10, 20)")
    results = TransactionsLoadQueries.load_transaction_in(connection)
    assert len(results) > 0, "No results returned"
    assert results[0].total == 200, f"Expected 200, got {results[0].total}"


def test_load_transaction_out(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'kg')")
    query.exec(
        "INSERT INTO customers VALUES (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars', NULL, NULL, NULL, NULL)"
    )
    query.prepare("""
        INSERT INTO transactions (
        id, type, customer_id, created_at, payment_type, is_invoiced
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """)
    query.addBindValue(1)
    query.addBindValue("OUT")
    query.addBindValue(1)
    query.addBindValue(get_timestamp())
    query.addBindValue(None)
    query.addBindValue(0)
    query.exec()
    query.exec("INSERT INTO transaction_items VALUES (1, 1, 1, 10, 20)")
    results = TransactionsLoadQueries.load_transactions_out(connection)
    assert len(results) > 0, "No results returned"
    assert results[0].total == 10.0, f"Expected 10.0, got {results[0].total}"


def test_load_transaction_in_respects_local_day_boundary(
    connection: QSqlDatabase, schema
) -> None:
    query = QSqlQuery(connection)

    query.exec("INSERT INTO commodities VALUES (1, 'kg')")
    query.exec(
        "INSERT INTO customers VALUES "
        "(1, 'Fake company', NULL, NULL, 'ICO123', 'Mars', NULL, NULL, NULL, NULL)"
    )
    query.exec("""
        INSERT INTO transactions
            (id, type, customer_id, created_at, payment_type, is_invoiced)
        VALUES
            (
                1, 'IN', 1,
                datetime('now', 'localtime', 'start of day', 'utc', '-1 second'),
                'TRANSFER', 0
            ),
            (
                2, 'IN', 1,
                datetime('now', 'localtime', 'start of day', 'utc'),
                'TRANSFER', 0
            ),
            (
                3, 'IN', 1,
                datetime('now', 'localtime', 'start of day', 'utc', '+1 day', '-1 second'),
                'TRANSFER', 0
            ),
            (
                4, 'IN', 1,
                datetime('now', 'localtime', 'start of day', 'utc', '+1 day'),
                'TRANSFER', 0
            )
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES
            (1, 1, 1, 10, 20),
            (2, 2, 1, 10, 20),
            (3, 3, 1, 10, 20),
            (4, 4, 1, 10, 20)
    """)
    results = TransactionsLoadQueries.load_transaction_in(connection)
    assert {transaction.transaction_id for transaction in results} == {2, 3}


def test_load_transaction_out_respects_local_day_boundary(
    connection: QSqlDatabase, schema
) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'kg')")
    query.exec(
        "INSERT INTO customers VALUES "
        "(1, 'Fake company', NULL, NULL, 'ICO123', 'Mars', NULL, NULL, NULL, NULL)"
    )
    query.exec("""
        INSERT INTO transactions
            (id, type, customer_id, created_at, payment_type, is_invoiced)
        VALUES
            (
                1, 'OUT', 1,
                datetime('now', 'localtime', 'start of day', 'utc', '-1 second'),
                NULL, 0
            ),
            (
                2, 'OUT', 1,
                datetime('now', 'localtime', 'start of day', 'utc'),
                NULL, 0
            ),
            (
                3, 'OUT', 1,
                datetime('now', 'localtime', 'start of day', 'utc', '+1 day', '-1 second'),
                NULL, 0
            ),
            (
                4, 'OUT', 1,
                datetime('now', 'localtime', 'start of day', 'utc', '+1 day'),
                NULL, 0
            )
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES
            (1, 1, 1, 10, 20),
            (2, 2, 1, 10, 20),
            (3, 3, 1, 10, 20),
            (4, 4, 1, 10, 20)
    """)
    results = TransactionsLoadQueries.load_transactions_out(connection)
    assert {transaction.transaction_id for transaction in results} == {2, 3}
