import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.tools_queries.database_backup_queries import (
    DatabaseBackupQueries,
)


@pytest.fixture
def connection() -> QSqlDatabase:
    connection = QSqlDatabase.addDatabase("QSQLITE", "backup_queries_test")
    connection.setDatabaseName(":memory:")
    connection.open()
    query = QSqlQuery(connection)
    query.exec("CREATE TABLE customers (id INTEGER PRIMARY KEY)")
    query.exec("CREATE TABLE categories (id INTEGER PRIMARY KEY)")
    query.exec("CREATE TABLE commodities (id INTEGER PRIMARY KEY)")
    query.exec("CREATE TABLE transactions (id INTEGER PRIMARY KEY)")
    return connection


def test_has_data_returns_false_when_database_is_empty(
    connection: QSqlDatabase,
) -> None:
    result = DatabaseBackupQueries.has_data(connection)
    assert result is False


@pytest.mark.parametrize(
    "table_name",
    [
        "customers",
        "categories",
        "commodities",
        "transactions",
    ],
)
def test_has_data_returns_true_when_data_exists(
    connection: QSqlDatabase,
    table_name: str,
) -> None:
    query = QSqlQuery(connection)
    query.exec(f"INSERT INTO {table_name} (id) VALUES (1)")
    result = DatabaseBackupQueries.has_data(connection)
    assert result is True
