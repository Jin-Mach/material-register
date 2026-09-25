from functools import partial

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.migration.column_migration import ColumnMigration
from material_register.services.error_handler import ErrorHandler


class DatabaseMigration:
    DB_VERSION = None
    MIGRATIONS_MAP = {
        1: [
            partial(
                ColumnMigration.add_column,
                table_name="transactions",
                column_name="is_invoiced",
                data_type="INTEGER",
                not_null=True,
                default=0,
                check="CHECK (is_invoiced IN (0, 1))",
            )
        ]
    }

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
        return True

    @classmethod
    def migrate(cls, db_connection: QSqlDatabase) -> bool:
        if cls.DB_VERSION is None:
            return False
        for version, migration_list in cls.MIGRATIONS_MAP.items():
            if cls.DB_VERSION >= version:
                continue
            for migration in migration_list:
                if not migration(db_connection):
                    ErrorHandler.handle_error(
                        f"{migration.func.__name__} failed.",
                        "db",
                        "critical",
                    )
                    return False
            query = QSqlQuery(db_connection)
            if not query.exec(f"PRAGMA user_version = {version}"):
                ErrorHandler.handle_error(
                    query.lastError().text(),
                    "db",
                    "critical",
                )
                return False
            cls.DB_VERSION = version
        return True
