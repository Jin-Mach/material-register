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


def test_create_transaction_success(
    connection,
    transaction_schema,
    items_schema,
    inventory_schema,
) -> None:
    dialog_data = {
        "transaction_type": "IN",
        "customer_id": 1,
        "payment_type": "CASH",
        "notes": "creation test",
    }
    items = [
        TransactionItem(
            commodity_id=2,
            unit_count=5,
            price_per_unit=10,
        )
    ]
    ok, error = TransactionsService.create_transaction(connection, dialog_data, items)
    assert ok is True
    assert error == ""
    query = QSqlQuery(connection)
    query.exec("SELECT COUNT(*) FROM transactions")
    assert query.next()
    assert query.value(0) == 1
    query.exec("SELECT commodity_id, unit_count, price_per_unit FROM transaction_items")
    assert query.next()
    assert query.value(0) == 2
    assert float(query.value(1)) == 5.0
    assert float(query.value(2)) == 10.0
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    assert float(query.value(0)) == 5.0


def test_create_transaction_invalid_transfer_type_rolls_back(
    connection,
    transaction_schema,
    items_schema,
    inventory_schema,
) -> None:
    dialog_data = {
        "transaction_type": "BAD_TYPE",
        "customer_id": 1,
        "payment_type": "CASH",
        "notes": "invalid transfer",
    }
    items = [
        TransactionItem(
            commodity_id=2,
            unit_count=3,
            price_per_unit=7,
        )
    ]
    ok, error = TransactionsService.create_transaction(connection, dialog_data, items)
    assert ok is False
    assert "Invalid transfer type" in error
    query = QSqlQuery(connection)
    query.exec("SELECT COUNT(*) FROM transactions")
    assert query.next()
    assert query.value(0) == 0
    query.exec("SELECT COUNT(*) FROM transaction_items")
    assert query.next()
    assert query.value(0) == 0
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    assert float(query.value(0)) == 0.0


def test_update_transaction_no_changes(
    connection,
    transaction_schema,
    items_schema,
    inventory_schema,
    old_dialog_data,
    old_items_data,
) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at, payment_type, notes
        ) VALUES (
            1, 'IN', 1, datetime('now'), 'CASH', 'old notes'
        )
    """)
    query.exec("""
        INSERT INTO transaction_items (
            transaction_id, commodity_id, unit_count, price_per_unit
        ) VALUES (
            1, 2, 10, 5
        )
    """)
    query.exec("UPDATE inventory SET stock = 10 WHERE commodity_id = 2")
    new_dialog_data = old_dialog_data.copy()
    new_items_data = old_items_data.copy()
    ok, error, changed = TransactionsService.update_transaction(
        connection, 1, new_dialog_data, old_dialog_data, new_items_data, old_items_data
    )
    assert ok is True
    assert error == ""
    assert changed is False
    query.exec("SELECT COUNT(*) FROM transactions")
    assert query.next()
    assert query.value(0) == 1
    query.exec("SELECT COUNT(*) FROM transaction_items")
    assert query.next()
    assert query.value(0) == 1
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    assert float(query.value(0)) == 10.0


def test_update_transaction_items_change_updates_inventory(
    connection,
    transaction_schema,
    items_schema,
    inventory_schema,
) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at, payment_type, notes
        ) VALUES (
            1, 'IN', 1, datetime('now'), 'CASH', 'old'
        )
    """)
    query.exec("""
        INSERT INTO transaction_items (
            transaction_id, commodity_id, unit_count, price_per_unit
        ) VALUES (
            1, 2, 2, 5
        )
    """)
    query.exec("UPDATE inventory SET stock = 5 WHERE commodity_id = 2")
    old_items = [TransactionItem(commodity_id=2, unit_count=2, price_per_unit=5)]
    new_items = [TransactionItem(commodity_id=2, unit_count=5, price_per_unit=5)]
    dialog_old = {
        "transaction_type": "IN",
        "customer_id": 1,
        "payment_type": "CASH",
        "notes": "old",
    }
    dialog_new = dialog_old.copy()
    ok, error, changed = TransactionsService.update_transaction(
        connection, 1, dialog_new, dialog_old, new_items, old_items
    )
    assert ok is True
    assert error == ""
    assert changed is True
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    assert float(query.value(0)) == 8.0


def test_update_transaction_items_aggregated_change(
    connection,
    transaction_schema,
    items_schema,
    inventory_schema,
) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at, payment_type, notes
        ) VALUES (
            1, 'IN', 1, datetime('now'), 'CASH', 'agg'
        )
    """)
    query.exec("""
        INSERT INTO transaction_items (
            transaction_id, commodity_id, unit_count, price_per_unit
        ) VALUES (1, 2, 2, 5), (1, 2, 3, 5)
    """)
    query.exec("UPDATE inventory SET stock = 10 WHERE commodity_id = 2")
    old_items = [
        TransactionItem(commodity_id=2, unit_count=2, price_per_unit=5),
        TransactionItem(commodity_id=2, unit_count=3, price_per_unit=5),
    ]
    new_items = [
        TransactionItem(commodity_id=2, unit_count=1, price_per_unit=5),
        TransactionItem(commodity_id=2, unit_count=1, price_per_unit=5),
    ]
    dialog_old = {
        "transaction_type": "IN",
        "customer_id": 1,
        "payment_type": "CASH",
        "notes": "agg",
    }
    dialog_new = dialog_old.copy()
    ok, error, changed = TransactionsService.update_transaction(
        connection, 1, dialog_new, dialog_old, new_items, old_items
    )
    assert ok is True
    assert error == ""
    assert changed is True
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    assert float(query.value(0)) == 7.0


def test_update_transaction_remove_all_items(
    connection,
    transaction_schema,
    items_schema,
    inventory_schema,
) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at, payment_type, notes
        ) VALUES (
            1, 'IN', 1, datetime('now'), 'CASH', 'remove'
        )
    """)
    query.exec("""
        INSERT INTO transaction_items (
            transaction_id, commodity_id, unit_count, price_per_unit
        ) VALUES (
            1, 2, 4, 5
        )
    """)
    query.exec("UPDATE inventory SET stock = 10 WHERE commodity_id = 2")
    old_items = [TransactionItem(commodity_id=2, unit_count=4, price_per_unit=5)]
    new_items: list[TransactionItem] = []
    dialog_old = {
        "transaction_type": "IN",
        "customer_id": 1,
        "payment_type": "CASH",
        "notes": "remove",
    }
    dialog_new = dialog_old.copy()
    ok, error, changed = TransactionsService.update_transaction(
        connection, 1, dialog_new, dialog_old, new_items, old_items
    )
    assert ok is True
    assert error == ""
    assert changed is True
    query.exec("SELECT COUNT(*) FROM transaction_items")
    assert query.next()
    assert query.value(0) == 0
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    assert float(query.value(0)) == 6.0


def test_delete_transaction_updates_inventory_and_removes_items(
    connection,
    transaction_schema,
    items_schema,
    inventory_schema,
) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT
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
    query.exec("INSERT INTO categories (id, name) VALUES (1, 'Cat')")
    query.exec(
        "INSERT INTO commodities (id, name, unit, category_id) VALUES (2, 'Apple', 'kg', 1)"
    )
    query.exec("""
        INSERT INTO transactions (
            id, type, customer_id, created_at, payment_type, notes
        ) VALUES (
            1, 'IN', 1, datetime('now'), 'CASH', 'to_delete'
        )
    """)
    query.exec("""
        INSERT INTO transaction_items (
            transaction_id, commodity_id, unit_count, price_per_unit
        ) VALUES (
            1, 2, 4, 10
        )
    """)
    query.exec("UPDATE inventory SET stock = 10 WHERE commodity_id = 2")
    query.exec("SELECT COUNT(*) FROM transactions")
    assert query.next()
    assert query.value(0) == 1
    query.exec("SELECT COUNT(*) FROM transaction_items")
    assert query.next()
    assert query.value(0) == 1
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    assert float(query.value(0)) == 10.0
    ok, error = TransactionsService.delete_transaction(connection, 1, "IN")
    assert ok is True
    assert error == ""
    query.exec("SELECT COUNT(*) FROM transactions")
    assert query.next()
    assert query.value(0) == 0
    query.exec("SELECT COUNT(*) FROM transaction_items")
    assert query.next()
    assert query.value(0) == 0
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 2")
    assert query.next()
    assert float(query.value(0)) == 6.0


def test_transactions_service_helpers_get_amount_and_stock_dict_and_final_dict() -> (
    None
):
    assert TransactionsService._get_amount("IN", 3) == 3
    assert TransactionsService._get_amount("OUT", 3) == -3
    assert TransactionsService._get_amount("IN", 3, negate=True) == -3
    assert TransactionsService._get_amount("OUT", 3, negate=True) == 3
    assert TransactionsService._get_amount("IN", 0) == 0
    items = [
        TransactionItem(commodity_id=1, unit_count=2, price_per_unit=0),
        TransactionItem(commodity_id=1, unit_count=3, price_per_unit=0),
        TransactionItem(commodity_id=2, unit_count=1, price_per_unit=0),
    ]
    stock_dict = TransactionsService._get_stock_dict(items)
    assert stock_dict[1] == 5
    assert stock_dict[2] == 1
    assert TransactionsService._get_stock_dict([]) == {}
    old_items = {1: 5, 2: 2}
    new_items = {1: 2, 3: 4}
    final_in = TransactionsService._get_final_stock_dict(old_items, new_items, "IN")
    assert final_in[1] == -3
    assert final_in[2] == -2
    assert final_in[3] == 4
    final_out = TransactionsService._get_final_stock_dict(old_items, new_items, "OUT")
    assert final_out[1] == 3
    assert final_out[2] == 2
    assert final_out[3] == -4
    no_change = TransactionsService._get_final_stock_dict({1: 2}, {1: 2}, "IN")
    assert no_change == {}
