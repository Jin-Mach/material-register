import uuid
from collections.abc import Generator, Iterator
from functools import partial
from pathlib import Path

import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.migration.column_migration import ColumnMigration
from material_register.db.migration.database_migration import DatabaseMigration


@pytest.fixture
def connection() -> Iterator[QSqlDatabase]:
    connection_name = f"test_database_migration_{uuid.uuid4().hex}"
    conn = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    conn.setDatabaseName(":memory:")
    assert conn.open()
    yield conn
    conn.close()
    del conn
    QSqlDatabase.removeDatabase(connection_name)


@pytest.fixture
def schema(connection: QSqlDatabase) -> None:
    query = QSqlQuery(connection)
    assert query.exec("""
        CREATE TABLE fake_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    del query


@pytest.fixture
def v0_database(tmp_path: Path) -> Iterator[QSqlDatabase]:
    database_path = tmp_path / "migration_v0.db"
    connection_name = f"migration_test_{uuid.uuid4().hex}"
    connection = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    connection.setDatabaseName(str(database_path))
    assert connection.open()
    query = QSqlQuery(connection)
    assert query.exec("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL
        )
    """)
    assert query.exec("PRAGMA user_version = 0")
    del query
    yield connection
    connection.close()
    del connection
    QSqlDatabase.removeDatabase(connection_name)


@pytest.fixture(autouse=True)
def restore_migrations_map() -> Generator[None]:
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
    assert query.exec("PRAGMA user_version")
    assert query.next()
    assert query.value(0) == 1


def test_migrate_real_database(v0_database: QSqlDatabase) -> None:
    assert DatabaseMigration.migration_init(v0_database)
    assert DatabaseMigration.DB_VERSION == 0
    assert not ColumnMigration.column_exists(v0_database, "transactions", "is_invoiced")
    assert DatabaseMigration.migrate(v0_database)
    assert DatabaseMigration.DB_VERSION == 1
    assert ColumnMigration.column_exists(v0_database, "transactions", "is_invoiced")
    query = QSqlQuery(v0_database)
    assert query.exec("PRAGMA table_info(transactions)")
    column_found = False
    while query.next():
        if query.value(1) == "is_invoiced":
            column_found = True
            assert query.value(2) == "INTEGER"
            assert query.value(3) == 1
            assert query.value(4) == "0"
    assert column_found


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
    del query
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
