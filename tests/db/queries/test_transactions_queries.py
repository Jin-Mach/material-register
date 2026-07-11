import pytest

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.transactions_queries import TransactionsQueries


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn

@pytest.fixture
def schema(connection) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            customer_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            payment_type TEXT,
            notes TEXT
        )
    """)

@pytest.fixture
def filter_schema(connection):
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            company TEXT,
            company_normalized TEXT,
            first_name_normalized TEXT,
            last_name_normalized TEXT,
            address TEXT,
            address_normalized TEXT,
            document_number TEXT
        )
    """)
    query.exec("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            customer_id INTEGER,
            created_at TEXT,
            payment_type TEXT,
            notes TEXT
        )
    """)
    query.exec("""
        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY,
            unit TEXT
        )
    """)
    query.exec("""
        CREATE TABLE transaction_items (
            transaction_id INTEGER,
            commodity_id INTEGER,
            unit_count INTEGER,
            price_per_unit REAL
        )
    """)

def test_insert_into_transactions(connection, schema) -> None:
    ok, error, transaction_id = TransactionsQueries.insert_into_transactions(
        connection, "IN", 1, "CASH", "notes"
    )
    assert ok is True
    assert error == ""
    assert isinstance(transaction_id, int)
    query = QSqlQuery(connection)
    query.exec("SELECT type, customer_id, payment_type, notes FROM transactions")
    assert query.next()
    assert query.value(0) == "IN"
    assert query.value(1) == 1
    assert query.value(2) == "CASH"
    assert query.value(3) == "notes"

def test_delete_transaction(connection, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (
            type, customer_id, created_at, payment_type, notes
        ) VALUES (
            'IN', 1, datetime('now'), 'CASH', 'to_delete'
        )
    """)
    query.exec("""
        INSERT INTO transactions (
            type, customer_id, created_at, payment_type, notes
        ) VALUES (
            'IN', 2, datetime('now'), 'CASH', 'not_delete'
        )
    """)
    query.exec("SELECT id FROM transactions ORDER BY id ASC")
    assert query.next()
    id_to_delete = query.value(0)
    assert query.next()
    id_to_check = query.value(0)
    query.exec("SELECT COUNT(*) FROM transactions")
    assert query.next()
    assert query.value(0) == 2
    ok, error = TransactionsQueries.delete_transaction(connection, id_to_delete)
    assert ok is True
    assert error == ""
    query.exec("SELECT COUNT(*) FROM transactions")
    assert query.next()
    assert query.value(0) == 1
    query.exec("SELECT id FROM transactions")
    assert query.next()
    assert query.value(0) == id_to_check

def test_update_transaction(connection, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (
            type, customer_id, created_at, payment_type, notes
        ) VALUES (
            'IN', 1, datetime('now'), 'CASH', 'old_notes'
        )
    """)
    query.exec("SELECT id FROM transactions")
    assert query.next()
    transaction_id = query.value(0)

    ok, error = TransactionsQueries.update_transaction(connection, transaction_id, "OUT", 2,
                                                       "TRANSFER", "updated_notes")
    assert ok is True
    assert error == ""
    query.prepare("""
        SELECT type, customer_id, payment_type, notes 
        FROM transactions
        WHERE id = ?
    """)
    query.addBindValue(transaction_id)
    query.exec()
    assert query.next()
    assert query.value(0) == "OUT"
    assert query.value(1) == 2
    assert query.value(2) == "TRANSFER"
    assert query.value(3) == "updated_notes"

def test_get_basic_filter_data(connection, filter_schema):
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO customers (
            id, first_name, last_name,
            first_name_normalized, last_name_normalized,
            address, address_normalized,
            document_number
        ) VALUES (
            1, 'Jürgen', 'Müller',
            'jurgen', 'muller',
            'Berlin', 'berlin',
            'DOC12345'
        )
    """)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at, payment_type, notes
        ) VALUES (
            1, 'IN', 1, datetime('now'), 'CASH', 'some note'
        )
    """)
    query.exec("""
        INSERT INTO customers (
            id, first_name, last_name,
            first_name_normalized, last_name_normalized,
            address, address_normalized,
            document_number
        ) VALUES (
            2, 'John', 'Smith',
            'john', 'smith',
            'London', 'london',
            'DOC99999'
        )
    """)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at, payment_type, notes
        ) VALUES (
            2, 'IN', 2, datetime('now'), 'CASH', 'some note'
        )
    """)
    query.exec("""
        INSERT INTO commodities (
            id, unit
        ) VALUES (
            1, 'kg'
        )
    """)
    query.exec("""
        INSERT INTO transaction_items (
            transaction_id, commodity_id,
            unit_count, price_per_unit
        ) VALUES
        (1, 1, 10, 5),
        (2, 1, 10, 5)
    """)
    result = TransactionsQueries.get_basic_filter_data(
        connection, "IN", "2000-01-01 00:00:00", "2100-01-01 00:00:00")
    assert isinstance(result, list)
    assert len(result) == 2
    row = result[0]
    assert row.customer_id in (1, 2)
    assert row.transaction_type == "IN"

def test_get_total_price(connection, filter_schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at, payment_type, notes
        ) VALUES (
            1, 'IN', 1, '2025-01-01 10:00:00', 'CASH', 't1'
        )
    """)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at, payment_type, notes
        ) VALUES (
            2, 'IN', 2, '2025-01-02 10:00:00', 'CASH', 't2'
        )
    """)
    query.exec("""
        INSERT INTO transaction_items (
            transaction_id, commodity_id,
            unit_count, price_per_unit
        ) VALUES
        (1, 1, 2, 10),   -- 20
        (2, 1, 3, 5)     -- 15
    """)
    total = TransactionsQueries.get_total_price(
        connection, "2025-01-01 00:00:00", "2025-12-31 23:59:59")
    assert isinstance(total, float)
    assert total == 35.0