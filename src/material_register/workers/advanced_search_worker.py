from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSql import QSqlDatabase

from material_register.domain.search_dataclass import SearchResultsDataclass
from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_ERROR, LOGGER_DB


class AdvancedSearchWorker(QObject):
    finished = Signal(SearchResultsDataclass)
    error = Signal(str)

    def __init__(
        self, where: str, having: str, params: list[str | int | float]
    ) -> None:
        super().__init__()
        self.where = where
        self.having = having
        self.params = params
        self.db_connection = None
        print("where:", self.where)
        print("having:", self.having)
        print("params:", self.params)

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
