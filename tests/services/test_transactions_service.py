import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.domain.transaction_item_dataclass import TransactionItem
from material_register.services.transactions_service import TransactionsService


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE")
    conn.setDatabaseName(":memory:")
    conn.open()
    query = QSqlQuery(conn)
    query.exec("PRAGMA foreign_keys = ON")
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
            price_per_unit REAL NOT NULL,
            FOREIGN KEY(transaction_id)
                REFERENCES transactions(id)
                ON DELETE CASCADE
        )
    """)


@pytest.fixture
def inventory_schema(connection) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE inventory (
            commodity_id INTEGER PRIMARY KEY,
            stock REAL NOT NULL
        )
    """)
    query.exec("""
        INSERT INTO inventory (commodity_id, stock)
        VALUES (2, 0)
    """)


@pytest.fixture
def old_dialog_data() -> dict[str, str | int]:
    return {
        "transaction_type": "IN",
        "customer_id": 1,
        "payment_type": "CASH",
        "notes": "old notes",
    }


@pytest.fixture
def old_items_data() -> list[TransactionItem]:
    return [
        TransactionItem(
            commodity_id=2,
            unit_count=10,
            price_per_unit=5,
        )
    ]


@pytest.mark.parametrize(
    "column_name,new_value",
    [
        ("customer_id", 2),
        ("payment_type", "CARD"),
        ("notes", "new notes"),
    ],
)
def test_update_transaction_header_changes(
    connection,
    transaction_schema,
    items_schema,
    inventory_schema,
    old_dialog_data,
    old_items_data,
    column_name,
    new_value,
) -> None:
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
        VALUES (1, 2, 10, 5)
    """)
    query.exec("""
        UPDATE inventory
        SET stock = 10
        WHERE commodity_id = 2
    """)
    new_dialog_data = old_dialog_data.copy()
    new_dialog_data[column_name] = new_value
    new_items_data = [
        TransactionItem(
            commodity_id=2,
            unit_count=10,
            price_per_unit=5,
        )
    ]
    ok, error, changed = TransactionsService.update_transaction(
        connection,
        1,
        new_dialog_data,
        old_dialog_data,
        new_items_data,
        old_items_data,
    )
    assert ok is True
    assert error == ""
    assert changed is True
    query.exec("""
        SELECT type, customer_id, payment_type, notes
        FROM transactions
        WHERE id = 1
    """)
    assert query.next()
    transaction_type = query.value(0)
    customer_id = query.value(1)
    payment_type = query.value(2)
    notes = query.value(3)
    assert transaction_type == "IN"
    if column_name == "customer_id":
        assert customer_id == 2
    else:
        assert customer_id == 1
    if column_name == "payment_type":
        assert payment_type == "CARD"
    else:
        assert payment_type == "CASH"
    if column_name == "notes":
        assert notes == "new notes"
    else:
        assert notes == "old notes"
