import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.database_setup import DatabaseSetup


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "foreign_keys_test")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


def test_foreign_keys_are_enabled(connection: QSqlDatabase) -> None:
    assert DatabaseSetup.setup_init(connection) is True
    query = QSqlQuery(connection)
    assert query.exec("PRAGMA foreign_keys")
    assert query.next()
    assert query.value(0) == 1


def test_is_new_database_returns_true_for_empty_database(
    connection: QSqlDatabase,
) -> None:
    is_new, error = DatabaseSetup.is_new_database(connection)
    assert is_new is True
    assert error == ""


def test_is_new_database_returns_false_when_customers_exists(
    connection: QSqlDatabase,
) -> None:
    query = QSqlQuery(connection)
    assert query.exec("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY
            )
    """)
    is_new, error = DatabaseSetup.is_new_database(connection)
    assert is_new is False
    assert error == ""
