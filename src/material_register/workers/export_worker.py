from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.db.queries.export_queries import ExportQueries
from material_register.init.db_init import DbInit


class ExportWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, export_settings: dict[str, Path | str | float | bool]) -> None:
        super().__init__()
        self.export_settings = export_settings
        self.db_connection = None

    @Slot()
    def run(self) -> None:
        from_date = self.export_settings["from_date"]
        to_date = self.export_settings["to_date"]
        ok, error, self.db_connection = DbInit.thread_connection("export_connection")
        if not ok:
            self.error.emit(error)
            return
        ok, error, in_data = ExportQueries.load_export_data_in(self.db_connection, from_date, to_date)
        if not ok:
            self.error.emit(error)
            return
        ok, error, out_data = ExportQueries.load_export_data_out(self.db_connection, from_date, to_date)
        if not ok:
            self.error.emit(error)
            return
        self.finished.emit()