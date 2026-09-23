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
