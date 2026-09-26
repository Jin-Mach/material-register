import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.migration.column_migration import ColumnMigration


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "column_migration_test")
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


@pytest.mark.parametrize(
    "table_name, column_name, result",
    [
        ("wrong_table", "name", False),
        ("fake_table", "name", True),
        ("fake_table", "notes", False),
    ],
    ids=[
        "non existing table",
        "existing table and existing column",
        "non existing column",
    ],
)
def test_column_exists(
    connection: QSqlDatabase,
    schema: None,
    table_name: str,
    column_name: str,
    result: bool,
) -> None:
    assert ColumnMigration.column_exists(connection, table_name, column_name) == result


@pytest.mark.parametrize(
    "table_name, result",
    [
        ("wrong_table", False),
        ("fake_table", True),
    ],
    ids=["non existing table", "existing table"],
)
def test_table_exists(
    connection: QSqlDatabase,
    schema: None,
    table_name: str,
    result: bool,
) -> None:
    assert ColumnMigration._table_exists(connection, table_name) == result


@pytest.mark.parametrize(
    "table_name, column_name, data_type, not_null, default, check, references, result",
    [
        ("fake_table", "notes", "TEXT", False, None, None, None, True),
        ("fake_table", "stock", "INTEGER", False, 0, None, None, True),
        ("fake_table", "active", "INTEGER", True, 1, None, None, True),
        (
            "fake_table",
            "valid",
            "INTEGER",
            False,
            None,
            "CHECK(valid >= 0)",
            None,
            True,
        ),
        (
            "fake_table",
            "category_id",
            "INTEGER",
            False,
            None,
            None,
            "REFERENCES fake_table(id)",
            True,
        ),
        ("wrong_table", "notes", "TEXT", False, None, None, None, False),
        ("fake_table", "invalid", "INTEGER", False, None, "fake check", None, False),
        (
            "fake_table",
            "invalid",
            "INTEGER",
            False,
            None,
            None,
            "fake references",
            False,
        ),
    ],
    ids=[
        "column only",
        "integer default",
        "not null with default",
        "check",
        "references",
        "non existing table",
        "invalid check",
        "invalid references",
    ],
)
def test_add_column(
    connection: QSqlDatabase,
    schema: None,
    table_name: str,
    column_name: str,
    data_type: str,
    not_null: bool,
    default: str | float | None,
    check: str | None,
    references: str | None,
    result: bool,
) -> None:
    column_added = ColumnMigration.add_column(
        connection,
        table_name,
        column_name,
        data_type,
        not_null,
        default,
        check,
        references,
    )
    assert column_added is result
    if result:
        assert (
            ColumnMigration.column_exists(connection, table_name, column_name) is True
        )


@pytest.mark.parametrize(
    "default, result",
    [
        ("CURRENT_TIME", (False, "")),
        ("TEXT", (True, "'TEXT'")),
        ("  TEXT  ", (True, "'TEXT'")),
        (0, (True, 0)),
    ],
    ids=[
        "wrong default",
        "text default",
        "text with spaces default",
        "integer default",
    ],
)
def test_validate_default(
    default: str | int, result: tuple[bool, str | int | float]
) -> None:
    default_result = ColumnMigration._validate_default(default)
    assert default_result == result


@pytest.mark.parametrize(
    "check, result",
    [
        ("fake check", (False, "")),
        ("CHECK(id > 0)", (True, "CHECK(id > 0)")),
    ],
    ids=["fake check", "check ok"],
)
def test_validate_check(check: str, result: tuple[bool, str]) -> None:
    check_result = ColumnMigration._validate_check(check)
    assert check_result == result


@pytest.mark.parametrize(
    "references, result",
    [
        ("fake references", (False, "")),
        ("references categories(id)", (False, "")),
        ("REFERENCES categories(id)", (True, "REFERENCES categories(id)")),
    ],
    ids=["fake references", "lower references", "references ok"],
)
def test_validate_references(references: str, result: tuple[bool, str]) -> None:
    references_result = ColumnMigration._validate_references(references)
    assert references_result == result
