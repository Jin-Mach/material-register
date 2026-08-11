import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.category_queries import CategoryQueries
from material_register.domain.category_dataclass import Category


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


def test_create_category(connection, schema) -> None:
    ok, error, category_id = CategoryQueries.create_category(connection, "test", "note")
    assert ok is True
    assert error == ""
    assert category_id is not None
    assert isinstance(category_id, int)
    query = QSqlQuery(connection)
    query.exec("SELECT name, notes FROM categories")
    assert query.next()
    assert query.value(0) == "test"
    assert query.value(1) == "note"


def test_update_category(connection, schema) -> None:
    CategoryQueries.create_category(connection, "old", "note")
    query = QSqlQuery(connection)
    query.exec("SELECT id FROM categories WHERE name='old'")
    query.next()
    category_id = query.value(0)
    ok, error = CategoryQueries.update_category(
        connection, category_id, "new", "updated"
    )
    assert ok is True
    assert error == ""
    query = QSqlQuery(connection)
    query.prepare("SELECT name, notes FROM categories WHERE id=?")
    query.addBindValue(category_id)
    query.exec()
    assert query.next()
    assert query.value(0) == "new"
    assert query.value(1) == "updated"


def test_get_categories(connection, schema) -> None:
    CategoryQueries.create_category(connection, "A", "n1")
    CategoryQueries.create_category(connection, "B", "n2")
    data = CategoryQueries.get_categories(connection)
    assert len(data) == 2
    assert data == [
        Category(id=1, name="A", notes="n1"),
        Category(id=2, name="B", notes="n2"),
    ]


def test_category_exists(connection, schema) -> None:
    CategoryQueries.create_category(connection, "A", "n")
    assert CategoryQueries.category_exists(connection, "A") is True
    assert CategoryQueries.category_exists(connection, "B") is False


def test_category_exists_ignored_id(connection, schema) -> None:
    CategoryQueries.create_category(connection, "A", "n")
    query = QSqlQuery(connection)
    query.exec("SELECT id FROM categories WHERE name='A'")
    query.next()
    cat_id = query.value(0)
    assert CategoryQueries.category_exists(connection, "A", ignored_id=cat_id) is False


def test_get_category_by_id(connection, schema) -> None:
    CategoryQueries.create_category(connection, "A", "note")
    query = QSqlQuery(connection)
    query.exec("SELECT id FROM categories WHERE name='A'")
    query.next()
    cat_id = query.value(0)
    data = CategoryQueries.get_category_by_id(connection, cat_id)
    assert data.name == "A"
    assert data.notes == "note"
    assert data.id == cat_id


def test_get_category_by_id_not_found(connection, schema) -> None:
    data = CategoryQueries.get_category_by_id(connection, 999)
    assert data is None
