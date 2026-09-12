import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.create_connection import create_db_tables
from material_register.db.utils.database_validator import (
    are_foreign_keys_valid,
    is_integrity_valid,
    is_schema_valid,
)


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


def test_integrity_is_valid(connection: QSqlDatabase) -> None:
    assert is_integrity_valid(connection) == (True, "")


def test_foreign_keys_are_valid(connection: QSqlDatabase) -> None:
    assert are_foreign_keys_valid(connection) == (True, [])


def test_foreign_key_is_invalid(empty_connection: QSqlDatabase) -> None:
    query = QSqlQuery(empty_connection)
    query.exec("""
        CREATE TABLE parent (
            id INTEGER PRIMARY KEY
        )
    """)
    query.exec("""
        CREATE TABLE child (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES parent(id)
        )
    """)
    query.exec("INSERT INTO child (id, parent_id) VALUES (1, 999)")
    valid, errors = are_foreign_keys_valid(empty_connection)
    assert valid is False
    assert len(errors) == 1


def test_multiple_foreign_keys_are_invalid(empty_connection: QSqlDatabase) -> None:
    query = QSqlQuery(empty_connection)
    query.exec("""
        CREATE TABLE parent (
            id INTEGER PRIMARY KEY
        )
    """)
    query.exec("""
        CREATE TABLE child (
            id INTEGER PRIMARY KEY,
            parent_id INTEGER,
            FOREIGN KEY (parent_id) REFERENCES parent(id)
        )
    """)
    query.exec("INSERT INTO child (id, parent_id) VALUES (1, 999)")
    query.exec("INSERT INTO child (id, parent_id) VALUES (2, 888)")
    valid, errors = are_foreign_keys_valid(empty_connection)
    assert valid is False
    assert len(errors) == 2
