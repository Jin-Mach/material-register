from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer
from PySide6.QtWidgets import QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_CRITICAL, LOGGER_DB
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.workers.inventory_history_worker import InventoryHistoryWorker

if TYPE_CHECKING:
    from material_register.ui.inventory.inventory_widget import InventoryWidget


class InventoryHistoryController(QObject):
    def __init__(self, inventory_widget: "InventoryWidget") -> None:
        super().__init__(inventory_widget)
        self.inventory_widget = inventory_widget
        self.inventory_history_widget = self.inventory_widget.inventory_history_widget
        self.worker = None
        self.thread = None

    def reload_commodity_history(
        self, commodity_id: int, from_date: str, to_date: str
    ) -> None:
        if self.thread is not None or self.worker is not None:
            return
        self.thread = QThread()
        self.worker = InventoryHistoryWorker(commodity_id, from_date, to_date)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._search_error)
        self.worker.finished.connect(self._search_ok)
        self.thread.start()

    def _search_error(self, error: str) -> None:
        self._clean_thread()
        QTimer.singleShot(100, lambda: self._finish_search(error=error))

    def _search_ok(self) -> None:
        self._clean_thread()
        QTimer.singleShot(100, lambda: self._finish_search())

    def _clean_thread(self) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _reset_variables(self) -> None:
        self.worker = None
        self.thread = None

    def _finish_search(self, error: str | None = None) -> None:
        self._reset_variables()
        if error is not None:
            print("error:", error)
            InventoryHistoryController._handle_search_error(
                error,
                f"{self.__class__.__name__}._search_error",
                self.inventory_widget,
            )
            return
        print("OK")

    @staticmethod
    def _handle_search_error(error: str, method: str, parent: QWidget) -> None:
        if not error:
            error = f"Unknown database error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", LOGGER_DB, LOG_LEVEL_CRITICAL)
        ErrorDialog(parent).show_dialog("DATABASE_ERROR", False)
