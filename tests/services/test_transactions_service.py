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
            commodityId=2,
            unitCount=10,
            pricePerUnit=12.5
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