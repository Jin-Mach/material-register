import sqlite3
import uuid
from contextlib import closing
from pathlib import Path

from PySide6.QtSql import QSqlDatabase

from material_register.db.create_connection import create_db_tables
from material_register.workers.tools_workers.database_restore_worker import (
    DatabaseRestoreWorker,
)


def create_valid_database(database_path: Path, category_name: str) -> None:
    connection_name = f"test_database_restore_{uuid.uuid4().hex}"
    connection = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    connection.setDatabaseName(str(database_path))
    assert connection.open()
    created, query = create_db_tables(connection)
    assert created, query.lastError().text()
    del query
    connection.close()
    del connection
    QSqlDatabase.removeDatabase(connection_name)
    with closing(sqlite3.connect(database_path)) as database, database:
        database.execute("INSERT INTO categories (name) VALUES (?)", (category_name,))


def read_category_names(database_path: Path) -> list[str]:
    with closing(sqlite3.connect(database_path)) as database, database:
        cursor = database.execute("SELECT name FROM categories ORDER BY name")
        return [row[0] for row in cursor.fetchall()]


def test_restore_worker_restores_valid_backup_and_emits_finished(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "database.db"
    restore_path = tmp_path / "restore.db"
    create_valid_database(database_path, "original")
    create_valid_database(restore_path, "restored")
    finished: list[bool] = []
    errors: list[str] = []
    worker = DatabaseRestoreWorker(database_path, restore_path)
    worker.finished.connect(lambda: finished.append(True))
    worker.error.connect(errors.append)
    worker.run()
    assert finished == [True]
    assert errors == []
    assert read_category_names(database_path) == ["restored"]


def test_restore_worker_rejects_invalid_schema_and_preserves_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "database.db"
    restore_path = tmp_path / "invalid_schema.db"
    create_valid_database(database_path, "original")
    with closing(sqlite3.connect(restore_path)) as database, database:
        database.execute("CREATE TABLE customers (id INTEGER PRIMARY KEY)")
    finished: list[bool] = []
    errors: list[str] = []
    worker = DatabaseRestoreWorker(database_path, restore_path)
    worker.finished.connect(lambda: finished.append(True))
    worker.error.connect(errors.append)
    worker.run()
    assert finished == []
    assert len(errors) == 1
    assert "Schema mismatch" in errors[0]
    assert read_category_names(database_path) == ["original"]


def test_restore_worker_rejects_invalid_foreign_keys_and_preserves_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "database.db"
    restore_path = tmp_path / "invalid_foreign_key.db"
    create_valid_database(database_path, "original")
    create_valid_database(restore_path, "invalid backup")
    with closing(sqlite3.connect(restore_path)) as database, database:
        database.execute(
            "INSERT INTO commodities (name, category_id) VALUES (?, ?)",
            ("invalid commodity", 999),
        )
    finished: list[bool] = []
    errors: list[str] = []
    worker = DatabaseRestoreWorker(database_path, restore_path)
    worker.finished.connect(lambda: finished.append(True))
    worker.error.connect(errors.append)
    worker.run()
    assert finished == []
    assert len(errors) == 1
    assert read_category_names(database_path) == ["original"]
