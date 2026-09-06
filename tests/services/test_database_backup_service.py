import sqlite3

from material_register.services.database_backup_service import DatabaseBackupService


def create_test_database(database_path):
    with sqlite3.connect(database_path) as database:
        database.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        database.execute("INSERT INTO test VALUES (1, 'Test')")
        database.commit()


def test_create_month_backup(tmp_path):
    database_path = tmp_path / "database.db"
    create_test_database(database_path)
    result = DatabaseBackupService.create_month_backup(
        database_path, month=2, year=2026
    )
    backup_path = tmp_path / "backup" / "2026" / "02.db"
    assert result is True
    assert backup_path.exists()
    with sqlite3.connect(backup_path) as database:
        cursor = database.execute("SELECT id, name FROM test")
        for row in cursor:
            assert row[0] == 1
            assert row[1] == "Test"


def test_create_month_backup_when_backup_exists(tmp_path):
    database_path = tmp_path / "database.db"
    create_test_database(database_path)
    backup_directory = tmp_path / "backup" / "2026"
    backup_directory.mkdir(parents=True)
    backup_path = backup_directory / "02.db"
    backup_path.touch()
    result = DatabaseBackupService.create_month_backup(
        database_path, month=2, year=2026
    )
    assert result is False


def test_create_year_backup(tmp_path):
    database_path = tmp_path / "database.db"
    create_test_database(database_path)
    result = DatabaseBackupService.create_year_backup(database_path, year=2025)
    backup_path = tmp_path / "backup" / "2025" / "backup_2025.db"
    assert result is True
    assert backup_path.exists()
    with sqlite3.connect(backup_path) as database:
        cursor = database.execute("SELECT id, name FROM test")
        for row in cursor:
            assert row[0] == 1
            assert row[1] == "Test"


def test_create_year_backup_removes_month_backups(tmp_path):
    database_path = tmp_path / "database.db"
    create_test_database(database_path)
    backup_directory = tmp_path / "backup" / "2025"
    backup_directory.mkdir(parents=True)
    (backup_directory / "01.db").touch()
    (backup_directory / "02.db").touch()
    (backup_directory / "03.db").touch()
    result = DatabaseBackupService.create_year_backup(database_path, year=2025)
    assert result is True
    assert (backup_directory / "backup_2025.db").exists()
    assert not (backup_directory / "01.db").exists()
    assert not (backup_directory / "02.db").exists()
    assert not (backup_directory / "03.db").exists()


def test_create_year_backup_when_backup_exists(tmp_path):
    database_path = tmp_path / "database.db"
    create_test_database(database_path)
    backup_directory = tmp_path / "backup" / "2025"
    backup_directory.mkdir(parents=True)
    backup_path = backup_directory / "backup_2025.db"
    backup_path.touch()
    result = DatabaseBackupService.create_year_backup(database_path, year=2025)
    assert result is False
