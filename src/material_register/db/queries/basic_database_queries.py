from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_CRITICAL, LOGGER_DB


class BasicDatabaseQueries:
    @staticmethod
    def get_transactions_count(db_connection: QSqlDatabase) -> tuple[bool, int]:
        query = QSqlQuery(db_connection)
        if not query.exec("SELECT COUNT(*) FROM transactions"):
            ErrorHandler.handle_error(
                query.lastError().text(), LOGGER_DB, LOG_LEVEL_CRITICAL
            )
            return False, 0
        transactions_count = 0
        if query.next():
            transactions_count = query.value(0)
        return True, transactions_count
