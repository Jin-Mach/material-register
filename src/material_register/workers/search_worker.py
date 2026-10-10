from PySide6.QtCore import QObject, Signal, Slot

from material_register.db.queries.search_queries import SearchQueries
from material_register.domain.search_dataclass import SearchResultsDataclass
from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_ERROR, LOGGER_DB


class SearchWorker(QObject):
    finished = Signal(SearchResultsDataclass)
    error = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        self.db_connection = None

    @Slot()
    def run(self) -> None:
        try:
            ok, error, self.db_connection = DbInit.thread_connection(
                "search_connection"
            )
            if not ok:
                self.error.emit(error)
                return
            ok, transactions = SearchQueries.load_transactions(self.db_connection)
            if not ok:
                self.error.emit("Transactions search query failed")
                return
            results_dataclass = SearchResultsDataclass(transactions=transactions)
            self.finished.emit(results_dataclass)
        except Exception as e:
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_ERROR)
            self.error.emit(f"Search failed: {e}")
