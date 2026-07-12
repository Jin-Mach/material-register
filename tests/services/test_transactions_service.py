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
def category_schema(connection) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    query.exec("""
        INSERT INTO categories (id, name)
        VALUES (1, 'test')
    """)

@pytest.fixture
def commodity_schema(connection) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            unit TEXT
        )
    """)
    query.exec("""
        INSERT INTO commodities (id, name, category_id, unit)
        VALUES (2, 'Test commodity', 1, 'kg')
    """)

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
def dialog_data() -> dict[str, str | int]:
    return {
        "transaction_type": "IN",
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

@pytest.mark.parametrize("transfer_type, insert_stock, expected_stock",
                         [("IN", 10, 10),
                          ("OUT", 10, -10)]
                         )
def test_create_transaction(connection, transaction_schema, items_schema, inventory_schema, dialog_data, items_data,
                            transfer_type, insert_stock, expected_stock) -> None:
    dialog_data["transaction_type"] = transfer_type
    items_data = [
        TransactionItem(
            commodity_id=2,
            unit_count=insert_stock,
            price_per_unit=12.5
        )
    ]
    ok, error = TransactionsService.create_transaction(connection, dialog_data, items_data)
    assert ok == True
    assert error == ""
    query = QSqlQuery(connection)
    query.exec("SELECT COUNT(*) FROM transactions")
    query.next()
    assert query.value(0) == 1
    query.exec("SELECT COUNT(*) FROM transaction_items")
    query.next()
    assert query.value(0) == 1
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    stock = query.value(0)
    assert stock == expected_stock

def test_update_transaction(connection, transaction_schema, items_schema, inventory_schema, dialog_data) -> None:
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
        INSERT INTO inventory (commodity_id, stock)
        VALUES (2, 0)
    """)
    updated_items_data = [
        TransactionItem(
            commodity_id=2,
            unit_count=999,
            price_per_unit=12.5
        )
    ]
    old_items_data = [
        TransactionItem(
            commodity_id=2,
            unit_count=10,
            price_per_unit=5
        )
    ]
    ok, error, changed = TransactionsService.update_transaction(connection, 1, dialog_data,
                                                                updated_items_data, old_items_data)
    assert ok is True
    assert error == ""
    assert changed is True
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
    query.exec("""
        SELECT stock FROM inventory WHERE commodity_id = 2
    """)
    assert query.next()
    assert query.value(0) == 989

def test_update_transaction_remove_item(connection, transaction_schema, items_schema, inventory_schema, dialog_data) -> None:
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
    old_items_data = [
        TransactionItem(
            commodity_id=2,
            unit_count=10,
            price_per_unit=5
        )
    ]
    new_items_data = []
    ok, error, changed = TransactionsService.update_transaction(connection, 1, dialog_data, new_items_data,
                                                                old_items_data)
    assert ok is True
    assert error == ""
    assert changed is True
    query.exec("""
        SELECT COUNT(*)
        FROM transaction_items
        WHERE transaction_id = 1
    """)
    assert query.next()
    assert query.value(0) == 0
    query.exec("""
        SELECT stock
        FROM inventory
        WHERE commodity_id = 2
    """)
    assert query.next()
    assert query.value(0) == 0

@pytest.mark.parametrize(
    "transfer_type, initial_stock, expected_stock",
    [
        ("IN", 10, 0),
        ("OUT", -10, 0),
    ],
)
def test_delete_transaction(connection, category_schema, commodity_schema, transaction_schema, items_schema, inventory_schema,
                            transfer_type, initial_stock, expected_stock) -> None:
    query = QSqlQuery(connection)
    query.exec(f"""
        UPDATE inventory
        SET stock = {initial_stock}
        WHERE commodity_id = 2
    """)
    assert query.lastError().text() == ""
    query.exec(f"""
        INSERT INTO transactions (
            id, type, customer_id, payment_type, notes
        )
        VALUES (1, '{transfer_type}', 1, 'CASH', 'notes')
    """)
    assert query.lastError().text() == ""
    query.exec("""
        INSERT INTO transaction_items (
            transaction_id, commodity_id, unit_count, price_per_unit
        )
        VALUES (1, 2, 10, 12.5)
    """)
    ok, error = TransactionsService.delete_transaction(connection, 1, transfer_type)
    assert ok is True
    assert error == ""
    query.exec("SELECT COUNT(*) FROM transactions")
    query.next()
    assert query.value(0) == 0
    query.exec("SELECT COUNT(*) FROM transaction_items")
    query.next()
    assert query.value(0) == 0
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    assert query.value(0) == expected_stock