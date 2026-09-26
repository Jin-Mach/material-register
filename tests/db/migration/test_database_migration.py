from functools import partial

import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.db_constants import DATABASE_NAME
from material_register.db.migration.column_migration import ColumnMigration
from material_register.db.migration.database_migration import DatabaseMigration
from material_register.db.utils.database_validator import (
    are_foreign_keys_valid,
    is_integrity_valid,
    is_schema_valid,
)
from material_register.providers.paths_provider import PathsProvider
from material_register.services.database_backup_service import DatabaseBackupService


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "migration_test")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


@pytest.fixture
def schema(connection: QSqlDatabase) -> None:
    query = QSqlQuery(connection)
    query.exec("""
                CREATE TABLE fake_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                )
            """)


@pytest.fixture(autouse=True)
def restore_migrations_map():
    original_map = DatabaseMigration.MIGRATIONS_MAP.copy()
    original_version = DatabaseMigration.DB_VERSION
    yield
    DatabaseMigration.MIGRATIONS_MAP = original_map
    DatabaseMigration.DB_VERSION = original_version


def test_migration_init_reads_db_version(connection: QSqlDatabase) -> None:
    assert DatabaseMigration.migration_init(connection) is True
    assert DatabaseMigration.DB_VERSION == 0


def test_set_db_version(connection: QSqlDatabase) -> None:
    query = QSqlQuery(connection)
    assert query.exec("PRAGMA user_version = 1") is True
    query.exec("PRAGMA user_version")
    query.next()
    assert query.value(0) == 1


def test_migrate_real_database() -> None:
    migration_table = "transactions"
    migration_column = "is_invoiced"
    root = PathsProvider.get_base_path()
    assert root is not None
    database_path = root / "database" / "history" / "material_register_V0.db"
    if not database_path.exists():
        pytest.skip("V0 database not available")
    database_test_path = (
        root / "database" / "database_test" / f"{DATABASE_NAME}_test.db"
    )
    database_test_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = DatabaseBackupService.create_custom_backup(
            database_path, database_test_path
        )
        assert result is True
        assert database_test_path.exists()
        connection = QSqlDatabase.addDatabase("QSQLITE", "migration_real_test")
        connection.setDatabaseName(str(database_test_path))
        assert connection.open() is True
        query = QSqlQuery(connection)
        assert query.exec("PRAGMA user_version") is True
        assert query.next() is True
        assert query.value(0) == 0
        assert (
            ColumnMigration.column_exists(connection, migration_table, migration_column)
            is False
        )
        query = QSqlQuery(connection)
        assert (
            query.exec(
                "SELECT id, type, customer_id, created_at, payment_type, notes FROM transactions ORDER BY id LIMIT 3"
            )
            is True
        )
        before = []
        while query.next():
            before.append(
                (
                    query.value(0),
                    query.value(1),
                    query.value(2),
                    query.value(3),
                    query.value(4),
                    query.value(5),
                )
            )
        assert DatabaseMigration.migration_init(connection) is True
        assert DatabaseMigration.DB_VERSION == 0
        assert DatabaseMigration.migrate(connection) is True
        assert DatabaseMigration.DB_VERSION == max(DatabaseMigration.MIGRATIONS_MAP)
        assert (
            ColumnMigration.column_exists(connection, migration_table, migration_column)
            is True
        )
        query = QSqlQuery(connection)
        assert query.exec("PRAGMA user_version") is True
        assert query.next() is True
        assert query.value(0) == max(DatabaseMigration.MIGRATIONS_MAP)
        schema_valid, error = is_schema_valid(connection)
        assert schema_valid, error
        integrity_valid, error = is_integrity_valid(connection)
        assert integrity_valid, error
        foreign_keys_valid, errors = are_foreign_keys_valid(connection)
        assert foreign_keys_valid, errors
        query = QSqlQuery(connection)
        assert (
            query.exec(
                "SELECT id, type, customer_id, created_at, payment_type, notes FROM transactions ORDER BY id LIMIT 3"
            )
            is True
        )
        after = []
        while query.next():
            after.append(
                (
                    query.value(0),
                    query.value(1),
                    query.value(2),
                    query.value(3),
                    query.value(4),
                    query.value(5),
                )
            )
        assert after == before
        query = QSqlQuery(connection)
        assert (
            query.exec(
                f"SELECT {migration_column} FROM {migration_table} ORDER BY id LIMIT 3"
            )
            is True
        )
        while query.next():
            assert query.value(0) == 0
    finally:
        if database_test_path.exists():
            database_test_path.unlink()


def test_migrate_without_db_version(connection: QSqlDatabase) -> None:
    DatabaseMigration.DB_VERSION = None
    result = DatabaseMigration.migrate(connection)
    assert result is False


def test_real_column_migration(connection: QSqlDatabase) -> None:
    query = QSqlQuery(connection)
    assert query.exec("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY
        )
    """)
    DatabaseMigration.DB_VERSION = 0
    result = DatabaseMigration.migrate(connection)
    assert result is True
    assert (
        ColumnMigration.column_exists(connection, "transactions", "is_invoiced") is True
    )
    assert DatabaseMigration.DB_VERSION == max(DatabaseMigration.MIGRATIONS_MAP)


@pytest.mark.parametrize(
    "table_name, column_name, data_type, not_null, default, check, references",
    [
        ("fake_table", "notes", "TEXT", False, None, None, None),
        ("fake_table", "stock", "INTEGER", False, 0, None, None),
        ("fake_table", "active", "INTEGER", True, 1, "CHECK(active IN (0, 1))", None),
        (
            "fake_table",
            "category_id",
            "INTEGER",
            False,
            None,
            None,
            "REFERENCES fake_table(id)",
        ),
    ],
    ids=["text column", "integer default", "checked column", "reference column"],
)
def test_migrate_column_variants(
    connection: QSqlDatabase,
    schema: None,
    table_name: str,
    column_name: str,
    data_type: str,
    not_null: bool,
    default: str | float | None,
    check: str | None,
    references: str | None,
) -> None:
    DatabaseMigration.MIGRATIONS_MAP = {
        1: [
            partial(
                ColumnMigration.add_column,
                table_name=table_name,
                column_name=column_name,
                data_type=data_type,
                not_null=not_null,
                default=default,
                check=check,
                references=references,
            )
        ]
    }
    DatabaseMigration.DB_VERSION = 0
    result = DatabaseMigration.migrate(connection)
    assert result is True
    assert ColumnMigration.column_exists(connection, table_name, column_name) is True
    assert DatabaseMigration.DB_VERSION == 1


def test_migrate_skips_current_version(connection: QSqlDatabase, schema: None) -> None:
    DatabaseMigration.MIGRATIONS_MAP = {
        1: [
            partial(
                ColumnMigration.add_column,
                table_name="fake_table",
                column_name="notes",
                data_type="TEXT",
            )
        ]
    }
    DatabaseMigration.DB_VERSION = 1
    result = DatabaseMigration.migrate(connection)
    assert result is True
    assert ColumnMigration.column_exists(connection, "fake_table", "notes") is False
    assert DatabaseMigration.DB_VERSION == 1


def test_migrate_multiple_versions(connection: QSqlDatabase, schema: None) -> None:
    DatabaseMigration.MIGRATIONS_MAP = {
        1: [
            partial(
                ColumnMigration.add_column,
                table_name="fake_table",
                column_name="notes",
                data_type="TEXT",
            )
        ],
        2: [
            partial(
                ColumnMigration.add_column,
                table_name="fake_table",
                column_name="active",
                data_type="INTEGER",
                not_null=True,
                default=1,
            )
        ],
    }
    DatabaseMigration.DB_VERSION = 0
    result = DatabaseMigration.migrate(connection)
    assert result is True
    assert ColumnMigration.column_exists(connection, "fake_table", "notes") is True
    assert ColumnMigration.column_exists(connection, "fake_table", "active") is True
    assert DatabaseMigration.DB_VERSION == 2


def test_migrate_fails_when_migration_fails(
    connection: QSqlDatabase, schema: None
) -> None:
    DatabaseMigration.MIGRATIONS_MAP = {
        1: [
            partial(
                ColumnMigration.add_column,
                table_name="unknown_table",
                column_name="notes",
                data_type="TEXT",
            )
        ]
    }
    DatabaseMigration.DB_VERSION = 0
    result = DatabaseMigration.migrate(connection)
    assert result is False
    assert DatabaseMigration.DB_VERSION == 0
