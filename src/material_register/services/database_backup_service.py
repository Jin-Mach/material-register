import sqlite3
from pathlib import Path

from material_register.services.error_handler import ErrorHandler


class DatabaseBackupService:
    @staticmethod
    def create_year_backup(database_path: Path, year: int) -> bool:
        try:
            backup_directory = DatabaseBackupService._get_backup_directory(
                database_path, year
            )
            backup_path = backup_directory / f"backup_{year}.db"
            if backup_path.exists():
                return False
            DatabaseBackupService._clear_year_folder(backup_directory)
            with sqlite3.connect(database_path) as database:
                with sqlite3.connect(backup_path) as backup:
                    database.backup(backup)
            return True
        except sqlite3.Error as e:
            ErrorHandler.handle_error(e, "db", "critical")
            return False
        except Exception as e:
            ErrorHandler.handle_error(e, "db", "critical")
            return False

    @staticmethod
    def create_month_backup(database_path: Path, month: int, year: int) -> bool:
        try:
            backup_directory = DatabaseBackupService._get_backup_directory(
                database_path, year
            )
            backup_path = backup_directory / f"{month:02}.db"
            if backup_path.exists():
                return False
            with sqlite3.connect(database_path) as database:
                with sqlite3.connect(backup_path) as backup:
                    database.backup(backup)
            return True
        except sqlite3.Error as e:
            ErrorHandler.handle_error(e, "db", "critical")
            return False
        except Exception as e:
            ErrorHandler.handle_error(e, "db", "critical")
            return False

    @staticmethod
    def _clear_year_folder(backup_path: Path) -> None:
        if any(backup_path.iterdir()):
            for path in backup_path.iterdir():
                path.unlink()

    @staticmethod
    def _get_backup_directory(database_path: Path, year: int) -> Path:
        backup_directory = database_path.parent / "backup" / str(year)
        backup_directory.mkdir(parents=True, exist_ok=True)
        return backup_directory
