import uuid
from pathlib import Path

from PySide6.QtSql import QSqlQuery

from material_register.db.create_connection import create_connection
from material_register.db.create_external_connection import (
    create_external_connection,
)


def test_external_connection_none() -> None:
    success, connection, error = create_external_connection(
        None, f"test_external_connection_{uuid.uuid4().hex}"
    )
    assert not success
    assert connection is None
    assert error


def test_external_connection_invalid_file(tmp_path: Path) -> None:
    database_file = tmp_path / "invalid.db"
    success, connection, error = create_external_connection(
        database_file, f"test_external_connection_{uuid.uuid4().hex}"
    )
    assert not success
    assert connection is None
    assert error


def test_external_connection_success(tmp_path: Path) -> None:
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    db = create_connection(
        db_dir, "test.db", f"test_create_connection_{uuid.uuid4().hex}"
    )
    assert db is not None
    db.close()
    del db

    success, connection, error = create_external_connection(
        db_dir / "test.db", f"test_external_connection_{uuid.uuid4().hex}"
    )
    assert success
    assert connection is not None
    assert not error

    query = QSqlQuery(connection)
    assert query.exec("SELECT name FROM sqlite_master WHERE type='table'")
    assert query.next()


def test_external_connection_read_only(tmp_path: Path) -> None:
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    db = create_connection(
        db_dir, "test.db", f"test_create_connection_{uuid.uuid4().hex}"
    )
    assert db is not None
    db.close()
    del db
    success, connection, _ = create_external_connection(
        db_dir / "test.db", f"test_external_connection_{uuid.uuid4().hex}"
    )
    assert success
    assert connection is not None
    query = QSqlQuery(connection)
    assert not query.exec("CREATE TABLE test_table (id INTEGER)")


def test_external_connection_unique_names(tmp_path: Path) -> None:
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    db = create_connection(
        db_dir, "test.db", f"test_create_connection_{uuid.uuid4().hex}"
    )
    assert db is not None
    db.close()
    del db
    success_1, connection_1, error_1 = create_external_connection(
        db_dir / "test.db", "test_external_connection"
    )
    success_2, connection_2, error_2 = create_external_connection(
        db_dir / "test.db", "test_external_connection"
    )
    assert success_1 and success_2
    assert connection_1 is not None
    assert connection_2 is not None
    assert not error_1 and not error_2
    assert connection_1.connectionName() != connection_2.connectionName()
