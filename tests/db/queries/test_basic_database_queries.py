import uuid

import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.basic_database_queries import BasicDatabaseQueries


@pytest.fixture
def connection() -> QSqlDatabase:
    connection_name = f"test_basic_database_queries_{uuid.uuid4().hex}"
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


def test_get_transactions_count(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (id, type)
        VALUES
            (1, 'IN'),
            (2, 'OUT'),
            (3, 'IN')
    """)
    success, transactions_count = BasicDatabaseQueries.get_transactions_count(
        connection
    )
    assert success is True
    assert transactions_count == 3


def test_get_transactions_count_query_error(connection: QSqlDatabase) -> None:
    success, transactions_count = BasicDatabaseQueries.get_transactions_count(
        connection
    )
    assert success is False
    assert transactions_count == 0
