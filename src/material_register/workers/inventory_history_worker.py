from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSql import QSqlDatabase

from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_ERROR, LOGGER_DB


class InventoryHistoryWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, commodity_id: int, from_date: str, to_date: str) -> None:
        super().__init__()
        self.commodity_id = commodity_id
        self.from_date = from_date
        self.to_date = to_date
        self.db_connection = None
        print("commodity_id:", commodity_id)
        print("from_date:", from_date)
        print("to_date:", to_date)

    @Slot()
    def run(self) -> None:
        try:
            ok, error, self.db_connection = DbInit.thread_connection(
                "history_search_connection"
            )
            if not ok:
                self.error.emit(error)
                return
            self.finished.emit()
        except Exception as e:
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_ERROR)
            self.error.emit(f"History search failed: {e}")
        finally:
            self._clean_db_connection()

    def _clean_db_connection(self) -> None:
        if self.db_connection is None:
            return
        connection = self.db_connection.connectionName()
        self.db_connection.close()
        self.db_connection = None
        QSqlDatabase.removeDatabase(connection)
