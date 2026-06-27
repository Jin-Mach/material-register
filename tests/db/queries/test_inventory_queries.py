import pytest

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.queries_constants import INVENTORY_QUERY


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
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            notes TEXT
        )
    """)
    query.exec("""
        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category_id INTEGER,
            unit TEXT DEFAULT 'kg',
            default_price REAL DEFAULT 0,
            notes TEXT,
            active INTEGER DEFAULT 1
        )
    """)
    query.exec("""
        CREATE TABLE inventory (
            commodity_id INTEGER PRIMARY KEY,
            stock REAL NOT NULL DEFAULT 0
        )
    """)


def test_get_inventory(connection, schema) -> None:
    insert_query = QSqlQuery(connection)
    insert_query.exec("""
        INSERT INTO categories (name, notes)
        VALUES ('category1', 'notes1')
    """)
    insert_query.exec("""
        INSERT INTO categories (name, notes)
        VALUES ('category2', 'notes2')
    """)
    insert_query.exec("""
        INSERT INTO commodities (name, category_id, unit, default_price, notes)
        VALUES ('commodity1', 1, 'kg', 11, 'notes')
    """)
    insert_query.exec("""
        INSERT INTO commodities (name, category_id, unit, default_price, notes)
        VALUES ('commodity2', 2, 'pcs', 22, 'notes')
    """)
    insert_query.exec("""
        INSERT INTO inventory (commodity_id, stock)
        VALUES (1, 11)
    """)
    insert_query.exec("""
        INSERT INTO inventory (commodity_id, stock)
        VALUES (2, 22)
    """)
    select_query = QSqlQuery(connection)
    select_query.exec(INVENTORY_QUERY)
    rows = []
    while select_query.next():
        rows.append((
            select_query.value(0),
            select_query.value(1),
            select_query.value(2),
            select_query.value(3),
        ))
    assert rows == [
        ("category1", "commodity1", "kg", 11),
        ("category2", "commodity2", "pcs", 22)
    ]