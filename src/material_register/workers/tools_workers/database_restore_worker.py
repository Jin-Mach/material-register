from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSql import QSqlDatabase

from material_register.db.utils.database_validator import (
    are_foreign_keys_valid,
    is_integrity_valid,
    is_schema_valid,
)
from material_register.services.database_backup_service import DatabaseBackupService


class DatabaseRestoreWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, database_path: Path, restore_path: Path) -> None:
        super().__init__()
        self.database_path = database_path
        self.restore_path = restore_path

    @Slot()
    def run(self) -> None:
        connection = QSqlDatabase.addDatabase("QSQLITE", "restore_connection")
        connection.setDatabaseName(str(self.restore_path))
        if not connection.open():
            self.error.emit("DATABASE_FAILED")
            QSqlDatabase.removeDatabase("restore_connection")
            return
        try:
            ok, error = is_integrity_valid(connection)
            if not ok:
                self.error.emit(error)
                return
            ok, error = is_schema_valid(connection)
            if not ok:
                self.error.emit(error)
                return
            ok, error = are_foreign_keys_valid(connection)
            if not ok:
                self.error.emit(error)
                return
        finally:
            connection.close()
            QSqlDatabase.removeDatabase("restore_connection")
        if not DatabaseBackupService.restore_database(
            self.database_path, self.restore_path
        ):
            self.error.emit("RESTORE_ERROR")
            return
        self.finished.emit()
