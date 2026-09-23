from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.utils.database_validator import (
    are_foreign_keys_valid,
    is_integrity_valid,
)
from material_register.services.error_handler import ErrorHandler


class DatabaseSetup:
    @staticmethod
    def setup_init(db_connection: QSqlDatabase) -> bool:
        query = QSqlQuery(db_connection)
        if not query.exec("PRAGMA foreign_keys = ON"):
            ErrorHandler.handle_error(query.lastError().text(), "db", "critical")
            return False
        if not query.exec("PRAGMA foreign_keys"):
            ErrorHandler.handle_error(query.lastError().text(), "db", "critical")
            return False
        if not query.next() or query.value(0) != 1:
            ErrorHandler.handle_error(
                "SQLite foreign key enforcement could not be enabled", "db", "critical"
            )
            return False
        ok, error = is_integrity_valid(db_connection)
        if not ok:
            ErrorHandler.handle_error(error, "db", "critical")
            return False
        ok, error = are_foreign_keys_valid(db_connection)
        if not ok:
            ErrorHandler.handle_error(error, "db", "critical")
            return False
        return True
