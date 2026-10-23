from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSql import QSqlDatabase

from material_register.db.queries.advanced_search_queries import AdvancedSearchQueries
from material_register.db.queries.basic_database_queries import BasicDatabaseQueries
from material_register.domain.adavanced_search_dataclass import AdvancedSearchDataclass
from material_register.domain.search_dataclass import SearchResultsDataclass
from material_register.init.db_init import DbInit
from material_register.services.advanced_filter_builder import AdvancedFilterBuilder
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_ERROR, LOGGER_DB


class AdvancedSearchWorker(QObject):
    finished = Signal(SearchResultsDataclass)
    error = Signal(str)

    def __init__(self, filters: list[AdvancedSearchDataclass]) -> None:
        super().__init__()
        self.filters = filters
        self.db_connection = None

    @Slot()
    def run(self) -> None:
        results_dataclass = None
        try:
            ok, error, self.db_connection = DbInit.thread_connection(
                "advanced_search_connection"
            )
            if not ok:
                self.error.emit(error)
                return
            transaction_where, transaction_having, transaction_count = (
                AdvancedFilterBuilder.create_advanced_filter(self.filters)
            )
            ok, transactions = AdvancedSearchQueries.load_transactions(
                self.db_connection,
                transaction_where,
                transaction_having,
                transaction_count,
            )
            if not ok:
                self.error.emit("Transactions advanced search query failed")
                return
            ok, count = BasicDatabaseQueries.get_transactions_count(self.db_connection)
            if not ok:
                self.error.emit("Transactions count query failed")
                return
            amount_where, amount_having, amount_count = (
                AdvancedFilterBuilder.create_advanced_filter(
                    self.filters, amount_having=True
                )
            )
            ok, amount = AdvancedSearchQueries.get_total_amount(
                self.db_connection, amount_where, amount_having, amount_count
            )
            if not ok:
                self.error.emit("Total amount query failed")
                return
            print("transactions:", transactions)
            print("count:", count)
            print("amount:", amount)
        except Exception as e:
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_ERROR)
            self.error.emit(f"Advanced search failed: {e}")
        finally:
            self._clean_db_connection()
        # if results_dataclass is not None:
        self.finished.emit(results_dataclass)

    def _clean_db_connection(self) -> None:
        if self.db_connection is None:
            return
        connection = self.db_connection.connectionName()
        self.db_connection.close()
        self.db_connection = None
        QSqlDatabase.removeDatabase(connection)
