from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer
from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import QWidget

from material_register.domain.search_dataclass import (
    SearchDataclass,
    SearchResultsDataclass,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_CRITICAL, LOGGER_DB
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.workers.search_worker import SearchWorker

if TYPE_CHECKING:
    from material_register.ui.search.search_widget import SearchWidget


class SearchController(QObject):
    def __init__(self, search_widget: "SearchWidget") -> None:
        super().__init__()
        self.search_widget = search_widget
        self.worker = None
        self.thread = None

    def start_thread(self) -> None:
        if self.thread is not None or self.worker is not None:
            return
        self._start_worker()

    def _start_worker(self) -> None:
        self.thread = QThread()
        self.worker = SearchWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._search_error)
        self.worker.finished.connect(self._search_ok)
        self.thread.start()

    def _search_error(self, error: str) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, lambda: self._finish_search(error=error))

    def _search_ok(self, results: SearchResultsDataclass) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, lambda: self._finish_search(results.transactions))

    def _clean_thread(self) -> None:
        if self.worker and self.worker.db_connection:
            connection_name = self.worker.db_connection.connectionName()
            self.worker.db_connection.close()
            self.worker.db_connection = None
            QSqlDatabase.removeDatabase(connection_name)
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _reset_variables(self) -> None:
        self.worker = None
        self.thread = None

    def _finish_search(
        self,
        transactions: list[SearchDataclass] | None = None,
        error: str | None = None,
    ) -> None:
        self._reset_variables()
        if error is not None:
            SearchController._handle_search_error(
                error, f"{self.__class__.__name__}._search_error", self.search_widget
            )
            return
        if transactions is None:
            transactions = []
        self.search_widget.search_transactions_model.load_data(transactions)

    @staticmethod
    def _handle_search_error(
        error: str, method: str, parent: QWidget, error_key: str = "SEARCH_ERROR"
    ) -> None:
        if not error:
            error = f"Unknown search error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", LOGGER_DB, LOG_LEVEL_CRITICAL)
        ErrorDialog(parent).show_dialog(error_key, False)
