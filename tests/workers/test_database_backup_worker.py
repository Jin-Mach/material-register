from datetime import UTC, datetime

from material_register.workers.database_backup_worker import DatabaseBackupWorker


def test_find_missing_backup_when_backup_directory_is_empty(tmp_path):
    backup_path = tmp_path / "backup"
    backup_path.mkdir()
    result = DatabaseBackupWorker._find_missing_backup(
        backup_path, datetime(2026, 2, 15, tzinfo=UTC)
    )
    assert result == (2025, None)


def test_find_missing_backup_when_year_backup_is_missing(tmp_path):
    backup_path = tmp_path / "backup"
    backup_path.mkdir()
    result = DatabaseBackupWorker._find_missing_backup(
        backup_path, datetime(2026, 5, 15, tzinfo=UTC)
    )
    assert result == (2025, None)


def test_find_missing_backup_in_january(tmp_path):
    backup_path = tmp_path / "backup"
    previous_year_path = backup_path / "2025"
    previous_year_path.mkdir(parents=True)
    (previous_year_path / "backup_2025.db").touch()
    result = DatabaseBackupWorker._find_missing_backup(
        backup_path, datetime(2026, 1, 15, tzinfo=UTC)
    )
    assert result == (None, None)


def test_find_missing_backup_when_month_backup_is_missing(tmp_path):
    backup_path = tmp_path / "backup"
    previous_year_path = backup_path / "2025"
    current_year_path = backup_path / "2026"
    previous_year_path.mkdir(parents=True)
    current_year_path.mkdir()
    (previous_year_path / "backup_2025.db").touch()
    result = DatabaseBackupWorker._find_missing_backup(
        backup_path, datetime(2026, 5, 15, tzinfo=UTC)
    )
    assert result == (2026, 4)


def test_find_missing_backup_when_month_backup_exists(tmp_path):
    backup_path = tmp_path / "backup"
    previous_year_path = backup_path / "2025"
    current_year_path = backup_path / "2026"
    previous_year_path.mkdir(parents=True)
    current_year_path.mkdir()
    (previous_year_path / "backup_2025.db").touch()
    (current_year_path / "04.db").touch()
    result = DatabaseBackupWorker._find_missing_backup(
        backup_path, datetime(2026, 5, 15, tzinfo=UTC)
    )
    assert result == (None, None)


def test_find_missing_backup_in_december(tmp_path):
    backup_path = tmp_path / "backup"
    previous_year_path = backup_path / "2025"
    current_year_path = backup_path / "2026"
    previous_year_path.mkdir(parents=True)
    current_year_path.mkdir()
    (previous_year_path / "backup_2025.db").touch()
    result = DatabaseBackupWorker._find_missing_backup(
        backup_path, datetime(2026, 12, 15, tzinfo=UTC)
    )
    assert result == (2026, 11)

def test_find_missing_backup_when_current_year_directory_is_missing(tmp_path):
    backup_path = tmp_path / "backup"
    previous_year_path = backup_path / "2025"
    previous_year_path.mkdir(parents=True)
    (previous_year_path / "backup_2025.db").touch()
    result = DatabaseBackupWorker._find_missing_backup(
        backup_path, datetime(2026, 5, 15, tzinfo=UTC)
    )
    assert result == (2026, 4)
