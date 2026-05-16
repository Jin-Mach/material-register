import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.catalog_queries import CatalogQueries


@pytest.fixture
def connection():
    conn = QSqlDatabase.addDatabase("QSQLITE")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


@pytest.fixture
def schema(connection):
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

def test_create_category(connection, schema):
    ok = CatalogQueries.create_category(connection, "test")
    assert ok is True
    query = QSqlQuery(connection)
    query.exec("SELECT name FROM categories")
    assert query.next()
    assert query.value(0) == "test"

def test_update_category(connection, schema):
    CatalogQueries.create_category(connection, "old")
    query = QSqlQuery(connection)
    query.exec("SELECT id FROM categories WHERE name='old'")
    query.next()
    category_id = query.value(0)
    ok = CatalogQueries.update_category(connection, category_id, "new")
    assert ok is True
    query = QSqlQuery(connection)
    query.prepare("SELECT name FROM categories WHERE id=?")
    query.addBindValue(category_id)
    query.exec()
    assert query.next()
    assert query.value(0) == "new"

def test_get_categories(connection, schema):
    CatalogQueries.create_category(connection, "A")
    CatalogQueries.create_category(connection, "B")
    data = CatalogQueries.get_categories(connection)
    assert len(data) == 2
    assert data == [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ]