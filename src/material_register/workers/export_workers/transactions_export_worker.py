from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.db.queries.export_queries.transactions_export_queries import (
    TransactionsExportQueries,
)
from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler

from material_register.services.export.excel.transactions_export.transactions_workbook import (
    TransactionsWorkbook,
)
from material_register.utils.system import is_disk_writable


class TransactionsExportWorker(QObject):
    finished = Signal()
    no_export_data = Signal(str)
    export_started = Signal()
    error = Signal(str)

    def __init__(
        self,
        export_settings: dict[str, Path | str | int | None | bool],
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
            customer_id = self.export_settings["customer_id"]
            ok, error, self.db_connection = DbInit.thread_connection(
                "transactions_export_connection"
            )
            if not ok:
                self.error.emit(error)
                return
            in_ok, in_error, in_data = TransactionsExportQueries.load_export_data(
                self.db_connection, from_date, to_date, customer_id, TRANSFER_IN
            )
            if not in_ok:
                self.no_export_data.emit(in_error)
                return
            out_ok, out_error, out_data = TransactionsExportQueries.load_export_data(
                self.db_connection, from_date, to_date, customer_id, TRANSFER_OUT
            )
            if not out_ok:
                self.no_export_data.emit(out_error)
            if not in_data and not out_data:
                self.no_export_data.emit("NO_DATA")
                return
            self.export_started.emit()
            workbook = TransactionsWorkbook.create_workbook(
                self.export_settings, self.export_texts, in_data, out_data
            )
            if not is_disk_writable(export_path.parent):
                self.error.emit(f"Export path {export_path} is not writable")
                return
            workbook.save(export_path)
            self.finished.emit()
        except Exception as e:
            ErrorHandler.handle_error(e, "export", "error")
            self.error.emit(f"Export failed: {e}")
