from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.inventory_queries_constants import (
    INVENTORY_HISTORY_DAILY_QUERY,
    INVENTORY_HISTORY_TOTAL_QUERY,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_CRITICAL, LOGGER_DB


class InventoryHistoryQueries:
    @staticmethod
    def get_inventory_history_data(
        db_connection: QSqlDatabase, commodity_id: int, from_date: str, to_date: str
    ) -> tuple[bool, list[list[str | float]]]:
        query = QSqlQuery(db_connection)
        query.prepare(INVENTORY_HISTORY_DAILY_QUERY)
        query.addBindValue(commodity_id)
        query.addBindValue(from_date)
        query.addBindValue(to_date)
        results = []
        if not query.exec():
            ErrorHandler.handle_error(
                query.lastError().text(), LOGGER_DB, LOG_LEVEL_CRITICAL
            )
            return False, results
        while query.next():
            results.append([query.value(0), query.value(1)])
        return True, results

    @staticmethod
    def get_inventory_history_total(
        db_connection: QSqlDatabase, commodity_id: int, from_date: str, to_date: str
    ) -> tuple[bool, float]:
        query = QSqlQuery(db_connection)
        query.prepare(INVENTORY_HISTORY_TOTAL_QUERY)
        query.addBindValue(commodity_id)
        query.addBindValue(from_date)
        query.addBindValue(to_date)
        total = 0.0
        if not query.exec():
            ErrorHandler.handle_error(
                query.lastError().text(), LOGGER_DB, LOG_LEVEL_CRITICAL
            )
            return False, total
        if query.next():
            total = query.value(0)
        return True, total
