from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.db.queries.export_queries import ExportQueries
from material_register.init.db_init import DbInit


class ExportWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, export_path: Path, from_date: str, to_date: str) -> None:
        super().__init__()
        self.export_path = export_path
        self.from_date = from_date
        self.to_date = to_date
        self.db_connection = None

    @Slot()
    def run(self) -> None:
        ok, error, self.db_connection = DbInit.thread_connection("export_connection")
        if not ok:
            self.error.emit(error)
            return
        ok, error, in_data = ExportQueries.load_export_data_in(self.db_connection, self.from_date, self.to_date)
        if not ok:
            self.error.emit(error)
            return
        ok, error, out_data = ExportQueries.load_export_data_out(self.db_connection, self.from_date, self.to_date)
        if not ok:
            self.error.emit(error)
            return
        self.finished.emit()