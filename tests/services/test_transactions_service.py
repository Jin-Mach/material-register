import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.domain.transaction_item_dataclass import TransactionItem
from material_register.services.transactions_service import TransactionsService


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn

@pytest.fixture
def transaction_schema(connection) -> None:
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
def items_schema(connection) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            commodity_id INTEGER NOT NULL,
            unit_count REAL NOT NULL,
            price_per_unit REAL NOT NULL
        )
    """)

@pytest.fixture
def dialog_data() -> dict[str, str | int]:
    return {
        "type": "IN",
        "customer_id": 1,
        "payment_type": "CASH",
        "notes": "some notes",
    }

@pytest.fixture
def items_data() -> list[TransactionItem]:
    return [
        TransactionItem(
            commodity_id=2,
            unit_count=10,
            price_per_unit=12.5
        )
    ]

def test_insert_new_transaction(connection, transaction_schema, items_schema, dialog_data, items_data) -> None:
    ok, error = TransactionsService.insert_new_transaction(connection, dialog_data, items_data)
    assert ok == True
    assert error == ""
    query = QSqlQuery(connection)
    query.exec("SELECT COUNT(*) FROM transactions")
    query.next()
    assert query.value(0) == 1
    query.exec("SELECT COUNT(*) FROM transaction_items")
    query.next()
    assert query.value(0) == 1

def test_update_transaction_with_items(connection, transaction_schema, items_schema, dialog_data) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, payment_type, notes
        )
        VALUES (1, 'IN', 1, 'CASH', 'old notes')
    """)
    query.exec("""
        INSERT INTO transaction_items (
            transaction_id, commodity_id, unit_count, price_per_unit
        )
        VALUES (1, 1, 10, 5)
    """)
    updated_items_data = [
        TransactionItem(
            commodity_id=2,
            unit_count=999,
            price_per_unit=12.5
        )
    ]
    ok, error = TransactionsService.update_transaction_with_items(connection, 1, dialog_data,
                                                                  updated_items_data)
    assert ok is True
    assert error == ""
    query.exec("""
        SELECT type, customer_id, payment_type, notes
        FROM transactions
        WHERE id = 1
    """)
    assert query.next()
    assert query.value(0) == "IN"
    assert query.value(1) == 1
    assert query.value(2) == "CASH"
    assert query.value(3) == "some notes"
    query.exec("""
        SELECT COUNT(*)
        FROM transaction_items
        WHERE transaction_id = 1
    """)
    assert query.next()
    assert query.value(0) == 1
    query.exec("""
        SELECT commodity_id, unit_count, price_per_unit
        FROM transaction_items
        WHERE transaction_id = 1
    """)
    assert query.next()
    assert query.value(0) == 2
    assert query.value(1) == 999
    assert query.value(2) == 12.5