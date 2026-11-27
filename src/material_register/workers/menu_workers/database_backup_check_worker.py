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
    error = Signal(str)

    def __init__(self, check_path: Path, custom_check: bool) -> None:
        super().__init__()
        self.check_path = check_path
        self.custom_check = custom_check
        self.db_connection = None

    @Slot()
    def run(self) -> None:
        start = PerformanceProvider.start()
        try:
            if self.custom_check:
                ok, error = self._check_external_database()
                if not ok:
                    self.error.emit(error)
                    return
            else:
                ok, error = self._check_database_backups()
                if not ok:
                    self.error.emit(error)
                    return
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._clean_db_connection()
            PerformanceProvider.stop(start, "DatabaseBackupCheckWorker.run")

    def _check_external_database(self) -> tuple[bool, str]:
        ok, self.db_connection, error = create_external_connection(
            self.check_path,
            "database_backup_check_connection",
        )
        if not ok:
            return False, error
        for validator in (
            is_integrity_valid,
            is_schema_valid,
            are_foreign_keys_valid,
        ):
            ok, error = validator(self.db_connection)
            if not ok:
                if isinstance(error, list):
                    error = "\n".join(error)
                return False, error
        return True, ""

    def _check_database_backups(self) -> tuple[bool, str]:
        for file in self.check_path.rglob("*.db"):
            if file.is_file():
                try:
                    ok, self.db_connection, error = create_external_connection(
                        file, "database_backup_check_connection"
                    )
                    if not ok:
                        return False, error
                    for validator in (
                        is_integrity_valid,
                        is_schema_valid,
                        are_foreign_keys_valid,
                    ):
                        ok, error = validator(self.db_connection)
                        if not ok:
                            if isinstance(error, list):
                                error = "\n".join(error)
                            return False, error
                finally:
                    self._clean_db_connection()
        return True, ""

    def _clean_db_connection(self) -> None:
        if self.db_connection is None:
            return
        connection = self.db_connection.connectionName()
        self.db_connection.close()
        self.db_connection = None
        QSqlDatabase.removeDatabase(connection)
