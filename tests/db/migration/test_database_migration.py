import pytest
from PySide6.QtSql import QSqlDatabase

from material_register.db.migration.database_migration import DatabaseMigration


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "migration_test")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


def test_migration_init_reads_db_version(connection: QSqlDatabase) -> None:
    assert DatabaseMigration.migration_init(connection) is True
    assert DatabaseMigration.DB_VERSION == 0
