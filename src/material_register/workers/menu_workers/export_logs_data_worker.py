from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.providers.performance_provider import PerformanceProvider


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
            print("logs path", self.logs_path)
            print("export path", self.export_path)
        except Exception as e:
            print(e)
            self.error.emit(str(e))
        finally:
            PerformanceProvider.stop(start, "ExportLogsDataWorker.run")
            self.finished.emit()
