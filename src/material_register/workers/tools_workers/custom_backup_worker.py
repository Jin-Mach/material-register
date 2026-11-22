from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.providers.performance_provider import PerformanceProvider
from material_register.services.database_backup_service import DatabaseBackupService


class CustomBackupWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, database_path: Path, backup_path: Path) -> None:
        super().__init__()
        self.database_path = database_path
        self.backup_path = backup_path

    @Slot()
    def run(self) -> None:
        start = PerformanceProvider.start()
        try:
            if not DatabaseBackupService.create_custom_backup(
                self.database_path, self.backup_path
            ):
                self.error.emit("BACKUP_ERROR")
                return
            self.finished.emit()
        finally:
            PerformanceProvider.stop(start, "CUSTOM_BACKUP_WORKER.run")
