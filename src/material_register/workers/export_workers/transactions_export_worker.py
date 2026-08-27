from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

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
            ok, error, self.db_connection = DbInit.thread_connection(
                "transactions_export_connection"
            )
            if not ok:
                self.error.emit(error)
                return
            print("Export path:", export_path)
            print("From:", from_date)
            print("To:", to_date)
            print("Settings:", self.export_settings)
            self.export_started.emit()
            self.finished.emit()
        except Exception as e:
            ErrorHandler.handle_error(e, "export", "error")
            self.error.emit(f"Export failed: {e}")
