from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.providers.performance_provider import PerformanceProvider
from material_register.services.menu_service.export_logs_data_service import (
    ExportLogsDataService,
)
from material_register.utils.system import is_disk_writable


class ExportLogsDataWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, logs_path: Path, export_path: Path) -> None:
        super().__init__()
        self.logs_path = logs_path
        self.export_path = export_path

    @Slot()
    def run(self) -> None:
        start = PerformanceProvider.start()
        try:
            if not is_disk_writable(self.export_path.parent):
                self.error.emit("BACKUP_ERROR")
                return
            ok, error = ExportLogsDataService.create_zip_file(
                self.logs_path, self.export_path
            )
            if not ok:
                self.error.emit(error)
                return
            self.finished.emit()
        except Exception as e:
            self.error.emit(f"Export logs data failed: {e}")
        finally:
            PerformanceProvider.stop(start, "ExportLogsDataWorker.run")
