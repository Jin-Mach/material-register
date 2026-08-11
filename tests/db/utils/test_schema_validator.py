import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.create_connection import create_db_tables
from material_register.db.utils.schema_validator import is_schema_valid


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "schema_test")
    conn.setDatabaseName(":memory:")
    conn.open()
    create_db_tables(conn)
    return conn


@pytest.fixture
def empty_connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "empty_schema_test")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


def test_schema_is_valid(connection: QSqlDatabase) -> None:
    assert is_schema_valid(connection) == (True, "")


def test_schema_missing_column(empty_connection: QSqlDatabase) -> None:
    query = QSqlQuery(empty_connection)
    query.exec("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY
        )
    """)
    valid, error = is_schema_valid(empty_connection)
    assert valid is False
    assert "Schema mismatch in table 'customers'" in error
    assert "Missing:" in error


def test_schema_extra_column(empty_connection: QSqlDatabase) -> None:
    query = QSqlQuery(empty_connection)
    query.exec("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            unexpected_column TEXT
        )
    """)
    valid, error = is_schema_valid(empty_connection)
    assert valid is False
    assert "customers" in error
    assert "unexpected_column" in error
