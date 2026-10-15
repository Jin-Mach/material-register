from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSql import QSqlDatabase

from material_register.db.queries.search_queries import SearchQueries
from material_register.domain.search_dataclass import SearchResultsDataclass
from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_ERROR, LOGGER_DB


class SearchWorker(QObject):
    finished = Signal(SearchResultsDataclass, bool)
    error = Signal(str)

    def __init__(self, where: str, params: list[str], init: bool = False) -> None:
        super().__init__()
        self.where = where
        self.params = params
        self.init = init
        self.db_connection: QSqlDatabase | None = None

    @Slot()
    def run(self) -> None:
        try:
            ok, error, self.db_connection = DbInit.thread_connection(
                "search_connection"
            )
            if not ok:
                self.error.emit(error)
                return
            ok, transactions = SearchQueries.load_transactions(
                self.db_connection, self.where, self.params
            )
            if not ok:
                self.error.emit("Transactions search query failed")
                return
            ok, count = SearchQueries.get_transactions_count(self.db_connection)
            if not ok:
                self.error.emit("Transactions count query failed")
                return
            ok, amount = SearchQueries.get_total_amount(
                self.db_connection, self.where, self.params
            )
            if not ok:
                self.error.emit("Total amount query failed")
                return
            ok, materials = SearchQueries.load_material(
                self.db_connection, self.where, self.params
            )
            if not ok:
                self.error.emit("Material query failed")
                return
            results_dataclass = SearchResultsDataclass(
                transactions=transactions,
                transactions_count=count,
                transactions_total_amount=amount,
                materials=materials,
            )
            self.finished.emit(results_dataclass, self.init)
        except Exception as e:
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_ERROR)
            self.error.emit(f"Search failed: {e}")
