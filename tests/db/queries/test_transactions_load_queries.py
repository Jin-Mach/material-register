import pytest

from datetime import datetime

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.transactions_load_queries import TransactionsLoadQueries


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
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def test_load_transaction_in(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'kg')")
    query.exec("INSERT INTO customers VALUES (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars', NULL, NULL, NULL, NULL)")
    query.prepare("""
        INSERT INTO transactions (id, type, customer_id, created_at, payment_type)
        VALUES (?, ?, ?, ?, ?)
    """)
    query.addBindValue(1)
    query.addBindValue('IN')
    query.addBindValue(1)
    query.addBindValue(get_timestamp())
    query.addBindValue('TRANSFER')
    query.exec()
    query.exec("INSERT INTO transaction_items VALUES (1, 1, 1, 10, 20)")
    results = TransactionsLoadQueries.load_transaction_in(connection)
    assert len(results) > 0, "No results returned"
    assert results[0].total == 200, f"Expected 200, got {results[0].total}"

def test_load_transaction_out(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'kg')")
    query.exec("INSERT INTO customers VALUES (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars', NULL, NULL, NULL, NULL)")
    query.prepare("""
        INSERT INTO transactions (id, type, customer_id, created_at, payment_type)
        VALUES (?, ?, ?, ?, ?)
    """)
    query.addBindValue(1)
    query.addBindValue('OUT')
    query.addBindValue(1)
    query.addBindValue(get_timestamp())
    query.addBindValue(None)
    query.exec()
    query.exec("INSERT INTO transaction_items VALUES (1, 1, 1, 10, 20)")
    results = TransactionsLoadQueries.load_transactions_out(connection)
    assert len(results) > 0, "No results returned"
    assert results[0].total == 10.0, f"Expected 10.0, got {results[0].total}"