from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSql import QSqlDatabase

from material_register.db.create_external_connection import create_external_connection
from material_register.db.utils.database_validator import (
    are_foreign_keys_valid,
    is_integrity_valid,
    is_schema_valid,
)
from material_register.providers.performance_provider import PerformanceProvider


class DatabaseBackupCheckWorker(QObject):
    finished = Signal()
    empty = Signal()
    invalid = Signal(list, str)
    error = Signal(str)

    def __init__(self, check_path: Path, custom_check: bool) -> None:
        super().__init__()
        self.check_path = check_path
        self.custom_check = custom_check
        self.db_connection = None
        self.invalid_files = []

    @Slot()
    def run(self) -> None:
        start = PerformanceProvider.start()
        try:
            if self.custom_check:
                ok, invalid_path, error = self._check_external_database()
                if not ok:
                    self.invalid_files.append(invalid_path)
                    self.invalid.emit(self.invalid_files, error)
                    return
            else:
                backups_exists = self._check_backups_exists()
                if not backups_exists:
                    self.empty.emit()
                    return
                ok, invalid_paths, error = self._check_database_backups()
                if not ok:
                    self.invalid_files.extend(invalid_paths)
                    self.invalid.emit(self.invalid_files, error)
                    return
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._clean_db_connection()
            PerformanceProvider.stop(start, "DatabaseBackupCheckWorker.run")

    def _check_external_database(self) -> tuple[bool, Path, str]:
        ok, self.db_connection, error = create_external_connection(
            self.check_path,
            "database_backup_check_connection",
        )
        if not ok:
            return False, self.check_path, error
        for validator in (
            is_integrity_valid,
            is_schema_valid,
            are_foreign_keys_valid,
        ):
            ok, error = validator(self.db_connection)
            if not ok:
                if isinstance(error, list):
                    error = "\n".join(error)
                return False, self.check_path, error
        return True, self.check_path, ""

    def _check_database_backups(self) -> tuple[bool, list[Path], str]:
        invalid_files = []
        errors = []
        is_check_valid = False
        for file in self.check_path.rglob("*.db"):
            if file.is_file():
                try:
                    ok, self.db_connection, error = create_external_connection(
                        file, "database_backup_check_connection"
                    )
                    if not ok:
                        invalid_files.append(file)
                        errors.append(f"{file} - {error}")
                        continue
                    for validator in (
                        is_integrity_valid,
                        is_schema_valid,
                        are_foreign_keys_valid,
                    ):
                        ok, error = validator(self.db_connection)
                        if not ok:
                            invalid_files.append(file)
                            if isinstance(error, list):
                                error = "\n".join(error)
                            errors.append(f"{file} - {error}")
                            break
                finally:
                    self._clean_db_connection()
        if len(invalid_files) == 0:
            is_check_valid = True
        return is_check_valid, invalid_files, "\n".join(errors)

    def _check_backups_exists(self) -> bool:
        for file in self.check_path.rglob("*.db"):
            if file.is_file():
                return True
        return False

    def _clean_db_connection(self) -> None:
        if self.db_connection is None:
            return
        connection = self.db_connection.connectionName()
        self.db_connection.close()
        self.db_connection = None
        QSqlDatabase.removeDatabase(connection)
