from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtSql import QSqlDatabase

from material_register.db.queries.inventory_history_queries import (
    InventoryHistoryQueries,
)
from material_register.domain.inventory_dataclass import InventoryHistoryDataclass
from material_register.init.db_init import DbInit
from material_register.providers.performance_provider import PerformanceProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_ERROR, LOGGER_DB


class InventoryHistoryWorker(QObject):
    finished = Signal(InventoryHistoryDataclass)
    error = Signal(str)

    def __init__(self, commodity_id: int, from_date: str, to_date: str) -> None:
        super().__init__()
        self.commodity_id = commodity_id
        self.from_date = from_date
        self.to_date = to_date
        self.db_connection = None

    @Slot()
    def run(self) -> None:
        start = PerformanceProvider.start()
        result_dataclass = None
        try:
            ok, error, self.db_connection = DbInit.thread_connection(
                "history_search_connection"
            )
            if not ok:
                self.error.emit(error)
                return
            ok, history_data = InventoryHistoryQueries.get_inventory_history_data(
                self.db_connection, self.commodity_id, self.from_date, self.to_date
            )
            if not ok:
                self.error.emit("Inventory history data query failed")
                return
            ok, total = InventoryHistoryQueries.get_inventory_history_total(
                self.db_connection, self.commodity_id, self.from_date, self.to_date
            )
            if not ok:
                self.error.emit("Inventory history total query failed")
                return
            result_dataclass = InventoryHistoryDataclass(
                history_data=history_data,
                total=total,
            )
        except Exception as e:
            ErrorHandler.handle_error(e, LOGGER_DB, LOG_LEVEL_ERROR)
            self.error.emit(f"History search failed: {e}")
        finally:
            self._clean_db_connection()
            PerformanceProvider.stop(start, "INVENTORY_HISTORY_WORKER.run")
        if result_dataclass is not None:
            self.finished.emit(result_dataclass)

    def _clean_db_connection(self) -> None:
        if self.db_connection is None:
            return
        connection = self.db_connection.connectionName()
        self.db_connection.close()
        self.db_connection = None
        QSqlDatabase.removeDatabase(connection)
