import shutil
import sqlite3
from contextlib import closing
from datetime import UTC, datetime
from pathlib import Path

from material_register.db.config.db_constants import DATABASE_NAME
from material_register.providers.paths_provider import PathsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_CRITICAL,
    LOGGER_DB,
)


class DatabaseBackupService:
    @staticmethod
    def create_year_backup(database_path: Path, year: int) -> bool:
        backup_path = None
        try:
            backup_directory = DatabaseBackupService._get_backup_directory(
                database_path, year
            )
            backup_path = backup_directory / f"backup_{year}.db"
            if backup_path.exists():
                return False
            with closing(sqlite3.connect(database_path)) as database, database:
                with closing(sqlite3.connect(backup_path)) as backup, backup:
                    database.backup(backup)
        except Exception as e:
            remove_error = DatabaseBackupService._remove_invalid_file(backup_path)
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_CRITICAL)
            if remove_error is not None:
                ErrorHandler.handle_error(remove_error, LOGGER_DB, LOG_LEVEL_CRITICAL)
            return False
        try:
            DatabaseBackupService._clear_year_folder(backup_directory, backup_path)
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_CRITICAL)
            return False

    @staticmethod
    def create_month_backup(database_path: Path, month: int, year: int) -> bool:
        backup_path = None
        try:
            backup_directory = DatabaseBackupService._get_backup_directory(
                database_path, year
            )
            backup_path = backup_directory / f"{month:02}.db"
            if backup_path.exists():
                return False
            with closing(sqlite3.connect(database_path)) as database, database:
                with closing(sqlite3.connect(backup_path)) as backup, backup:
                    database.backup(backup)
            return True
        except Exception as e:
            remove_error = DatabaseBackupService._remove_invalid_file(backup_path)
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_CRITICAL)
            if remove_error is not None:
                ErrorHandler.handle_error(remove_error, LOGGER_DB, LOG_LEVEL_CRITICAL)
            return False

    @staticmethod
    def create_custom_backup(database_path: Path, backup_path: Path) -> bool:
        backup_exists = backup_path.exists()
        try:
            with closing(sqlite3.connect(database_path)) as database, database:
                with closing(sqlite3.connect(backup_path)) as backup, backup:
                    database.backup(backup)
            return True
        except Exception as e:
            if not backup_exists:
                remove_error = DatabaseBackupService._remove_invalid_file(backup_path)
                if remove_error is not None:
                    ErrorHandler.handle_error(
                        remove_error, LOGGER_DB, LOG_LEVEL_CRITICAL
                    )
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_CRITICAL)
            return False

    @staticmethod
    def restore_database(database_path: Path, restore_path: Path) -> bool:
        try:
            with closing(sqlite3.connect(restore_path)) as backup, backup:
                with closing(sqlite3.connect(database_path)) as database, database:
                    backup.backup(database)
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_CRITICAL)
            return False

    @staticmethod
    def delete_backup_folder() -> bool:
        backup_folder = PathsProvider.database / "backup"
        if not backup_folder.exists():
            return True
        try:
            shutil.rmtree(backup_folder)
        except OSError as e:
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_CRITICAL)
            return False
        return True

    @staticmethod
    def delete_invalid_backup(invalid_backup: list[Path]) -> bool:
        database_path = (PathsProvider.database / DATABASE_NAME).with_suffix(".db")
        for backup_path in invalid_backup:
            if backup_path.resolve() == database_path.resolve():
                continue
            try:
                backup_path.unlink(missing_ok=True)
            except OSError as e:
                ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_CRITICAL)
                return False
        return True

    @staticmethod
    def _clear_year_folder(backup_directory: Path, backup_path: Path) -> None:
        if any(backup_directory.iterdir()):
            for path in backup_directory.iterdir():
                if path != backup_path:
                    path.unlink()

    @staticmethod
    def _get_backup_directory(database_path: Path, year: int) -> Path:
        backup_directory = database_path.parent / "backup" / str(year)
        backup_directory.mkdir(parents=True, exist_ok=True)
        return backup_directory

    @staticmethod
    def get_last_backup_date(backup_path: Path) -> datetime | None:
        created_at = None
        for file in backup_path.rglob("*.db"):
            file_created_at = file.stat().st_mtime
            if created_at is None or file_created_at > created_at:
                created_at = file_created_at
        if created_at is not None:
            return datetime.fromtimestamp(created_at, UTC)
        return None

    @staticmethod
    def get_backup_tree(backup_path: Path) -> dict[str, list[Path]]:
        backup_tree = {}
        for year in backup_path.iterdir():
            tree_name = year.stem
            backup_paths = list(year.glob("*.db"))
            if not backup_paths:
                continue
            backup_tree[tree_name] = backup_paths
        return backup_tree

    @staticmethod
    def _remove_invalid_file(backup_path: Path | None) -> str | None:
        try:
            if backup_path is None:
                return None
            backup_path.unlink(missing_ok=True)
            return None
        except OSError as e:
            return str(e)
