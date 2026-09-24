from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.services.error_handler import ErrorHandler


class DatabaseMigration:
    DB_VERSION = None

    @classmethod
    def migration_init(cls, db_connection: QSqlDatabase) -> bool:
        query = QSqlQuery(db_connection)
        if not query.exec("PRAGMA user_version"):
            ErrorHandler.handle_error(query.lastError().text(), "db", "critical")
            return False
        if not query.next():
            ErrorHandler.handle_error(query.lastError().text(), "db", "critical")
            return False
        cls.DB_VERSION = query.value(0)
        print("DB version: ", cls.DB_VERSION)
        return True
