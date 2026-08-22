from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.db.queries.export_queries.summary_export_queries import (
    SummaryExportQueries,
)
from material_register.init.db_init import DbInit
from material_register.services.export.excel.summary_export.summary_workbook import (
    SummaryWorkbook,
)
from material_register.utils.system import is_disk_writable


class SummaryExportWorker(QObject):
    finished = Signal(float)
    no_export_data = Signal(str)
    export_started = Signal()
    error = Signal(str)

    def __init__(
        self,
        export_settings: dict[str, Path | str | float | bool],
        export_texts: dict[str, dict[str, str]],
    ) -> None:
        super().__init__()
        self.export_settings = export_settings
        self.export_texts = export_texts
        self.db_connection = None

    @Slot()
    def run(self) -> None:
        try:
            export_path = self.export_settings["export_path"]
            from_date = self.export_settings["from_date"]
            to_date = self.export_settings["to_date"]
            ok, error, self.db_connection = DbInit.thread_connection(
                "export_connection"
            )
            if not ok:
                self.error.emit(error)
                return
            ok, error, in_data = SummaryExportQueries.load_export_data_in(
                self.db_connection, from_date, to_date
            )
            if not ok:
                self.error.emit(error)
                return
            ok, error, out_data = SummaryExportQueries.load_export_data_out(
                self.db_connection, from_date, to_date
            )
            if not ok:
                self.error.emit(error)
                return
            if not in_data and not out_data:
                self.no_export_data.emit("NO_DATA")
                return
            self.export_started.emit()
            workbook, last_balance = SummaryWorkbook.create_workbook(
                self.export_settings, self.export_texts, in_data, out_data
            )
            if not is_disk_writable(export_path.parent):
                self.error.emit(f"Export path {export_path} is not writable")
                return
            workbook.save(export_path)
            self.finished.emit(last_balance)
        except Exception as e:
            self.error.emit(f"Export failed: {e}")
