from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.providers.performance_provider import PerformanceProvider


class DatabaseBackupCheckWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, check_path: Path, custom_check: bool) -> None:
        super().__init__()
        self.check_path = check_path
        self.custom_check = custom_check

    @Slot()
    def run(self) -> None:
        start = PerformanceProvider.start()
        try:
            print("check path:", self.check_path)
            print("custom_check:", self.custom_check)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            PerformanceProvider.stop(start, "DatabaseBackupCheckWorker.run")
