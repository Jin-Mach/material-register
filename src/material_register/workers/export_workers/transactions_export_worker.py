from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.db.queries.export_queries.transactions_export_queries import (
    TransactionsExportQueries,
)
from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler


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
            print("export_settings:", self.export_settings)
            print("customer_id:", customer_id)
            print("customer_id type:", type(customer_id))
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
            print("in data:", in_data)
            out_ok, out_error, out_data = TransactionsExportQueries.load_export_data(
                self.db_connection, from_date, to_date, customer_id, TRANSFER_OUT
            )
            if not out_ok:
                self.no_export_data.emit(out_error)
                return
            print("out data:", out_data)
            self.export_started.emit()
            self.finished.emit()
        except Exception as e:
            ErrorHandler.handle_error(e, "export", "error")
            self.error.emit(f"Export failed: {e}")
