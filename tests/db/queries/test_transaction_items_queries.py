import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.transaction_items_queries import (
    TransactionItemsQueries,
)


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
        CREATE TABLE transaction_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id INTEGER NOT NULL,
            commodity_id INTEGER NOT NULL,
            unit_count REAL NOT NULL,
            price_per_unit REAL NOT NULL
        )
    """)

@pytest.mark.parametrize("transaction_id, commodity_id, unit_count, price_per_unit", [
    (1, 2, 1.5, 2.5),
    (2, 1, 1, 0),
], ids=["IN", "OUT"])
def test_insert_into_transaction_items(connection, schema, transaction_id, commodity_id, unit_count,
                                       price_per_unit) -> None:
    ok, error = TransactionItemsQueries.insert_into_transaction_items(connection, transaction_id, commodity_id,
                                                                  unit_count, price_per_unit)
    assert ok == True
    assert error == ""
    query = QSqlQuery(connection)
    query.exec("SELECT transaction_id, commodity_id, unit_count, price_per_unit FROM transaction_items")
    assert query.next()
    assert query.value(0) == transaction_id
    assert query.value(1) == commodity_id
    assert query.value(2) == unit_count
    assert query.value(3) == price_per_unit

def test_delete_transaction_items(connection, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transaction_items
        (transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES
            (1, 1, 10, 2.5),
            (1, 2, 5, 3.0),
            (2, 3, 1, 1.0)
    """)
    ok, error = TransactionItemsQueries.delete_transaction_items(connection, 1)
    assert ok is True
    assert error == ""
    query.exec("""
        SELECT COUNT(*)
        FROM transaction_items
        WHERE transaction_id = 1
    """)
    query.next()
    assert query.value(0) == 0
    query.exec("""
        SELECT COUNT(*)
        FROM transaction_items
        WHERE transaction_id = 2
    """)
    query.next()
    assert query.value(0) == 1

def test_get_transaction_items(connection, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transaction_items (transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES
            (1, 1, 10, 2.5),
            (1, 2, 3.5, 4.0)
    """)
    query.exec("""
        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY,
            name TEXT,
            unit TEXT,
            category_id INTEGER
        )
    """)
    query.exec("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    query.exec("INSERT INTO categories (id, name) VALUES (1, 'FE')")
    query.exec("INSERT INTO commodities (id, name, unit, category_id) VALUES (1, '12345', 'kg', 1)")
    query.exec("INSERT INTO commodities (id, name, unit, category_id) VALUES (2, '67890', 'ks', 1)")
    result = TransactionItemsQueries.get_transaction_items(connection, 1)
    assert len(result) == 2
    assert result[0].commodity_id == 1
    assert result[0].unit_count == 10
    assert result[0].price_per_unit == 2.5
    assert result[0].commodity_name == "12345"
    assert result[0].commodity_suffix == "kg"
    assert result[0].category_name == "FE"
    assert result[1].commodity_id == 2
    assert result[1].unit_count == 3.5
    assert result[1].price_per_unit == 4.0
    assert result[1].commodity_name == "67890"
    assert result[1].commodity_suffix == "ks"
    assert result[1].category_name == "FE"