import pytest

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.transaction_items_queries import TransactionItemsQueries


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