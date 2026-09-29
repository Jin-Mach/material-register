from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.utils.database_validator import (
    are_foreign_keys_valid,
    is_integrity_valid,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_CRITICAL,
    LOGGER_DB,
)


class DatabaseSetup:
    @staticmethod
    def setup_init(db_connection: QSqlDatabase) -> bool:
        query = QSqlQuery(db_connection)
        if not query.exec("PRAGMA foreign_keys = ON"):
            ErrorHandler.handle_error(
                query.lastError().text(), LOGGER_DB, LOG_LEVEL_CRITICAL
            )
            return False
        if not query.exec("PRAGMA foreign_keys"):
            ErrorHandler.handle_error(
                query.lastError().text(), LOGGER_DB, LOG_LEVEL_CRITICAL
            )
            return False
        if not query.next() or query.value(0) != 1:
            ErrorHandler.handle_error(
                "SQLite foreign key enforcement could not be enabled",
                LOGGER_DB,
                LOG_LEVEL_CRITICAL,
            )
            return False
        ok, error = is_integrity_valid(db_connection)
        if not ok:
            ErrorHandler.handle_error(error, LOGGER_DB, LOG_LEVEL_CRITICAL)
            return False
        ok, error = are_foreign_keys_valid(db_connection)
        if not ok:
            ErrorHandler.handle_error(error, LOGGER_DB, LOG_LEVEL_CRITICAL)
            return False
        return True

    @staticmethod
    def is_new_database(db_connection: QSqlDatabase) -> tuple[bool, str]:
        query = QSqlQuery(db_connection)
        if not query.exec(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='customers'"
        ):
            return False, query.lastError().text()
        return not query.next(), ""
