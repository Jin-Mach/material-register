from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.services.error_handler import ErrorHandler


class ColumnMigration:
    @staticmethod
    def column_exists(
        db_connection: QSqlDatabase, table_name: str, new_column: str
    ) -> bool:
        query = QSqlQuery(db_connection)
        if not query.exec(f"PRAGMA table_info({table_name})"):
            ErrorHandler.handle_error(query.lastError().text(), "db", "critical")
            return False
        while query.next():
            column_name = query.value(1)
            if column_name == new_column:
                return True
        return False

    @staticmethod
    def add_column(
        db_connection: QSqlDatabase,
        table_name: str,
        column_name: str,
        data_type: str,
        not_null: bool = False,
        default: str | float | None = None,
        check: str | None = None,
        references: str | None = None,
    ) -> bool:
        query = QSqlQuery(db_connection)
        if not ColumnMigration._table_exists(db_connection, table_name.strip()):
            ErrorHandler.handle_error(
                f"Table '{table_name.strip()}' does not exist", "db", "critical"
            )
            return False
        sql = f"ALTER TABLE {table_name.strip()} ADD COLUMN {column_name.strip()}"
        if data_type:
            sql += f" {data_type.strip()}"
        if not_null and (default is not None and default != ""):
            sql += " NOT NULL"
        if default is not None and default != "":
            ok, default = ColumnMigration._validate_default(default)
            if not ok:
                return False
            sql += f" DEFAULT {default}"
        if check:
            ok, check = ColumnMigration._validate_check(check)
            if not ok:
                return False
            sql += f" {check}"
        if references:
            ok, references = ColumnMigration._validate_references(references)
            if not ok:
                return False
            sql += f" {references}"
        if not query.exec(sql):
            ErrorHandler.handle_error(query.lastError().text(), "db", "critical")
            return False
        return True

    @staticmethod
    def _table_exists(db_connection: QSqlDatabase, table_name: str) -> bool:
        query = QSqlQuery(db_connection)
        if not query.exec(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        ):
            ErrorHandler.handle_error(query.lastError().text(), "db", "critical")
            return False
        return query.next()

    @staticmethod
    def _validate_default(default: str | float) -> tuple[bool, str | int | float]:
        if type(default) is str:
            stripped = default.strip()
            if stripped.upper() in [
                "CURRENT_TIME",
                "CURRENT_DATE",
                "CURRENT_TIMESTAMP",
            ]:
                ErrorHandler.handle_error(
                    "CURRENT time defaults are not supported with ADD COLUMN",
                    "db",
                    "critical",
                )
                return False, ""
            default = stripped.replace("'", "''")
            default = f"'{default}'"
        return True, default

    @staticmethod
    def _validate_check(check: str) -> tuple[bool, str]:
        if not check.startswith("CHECK (") or not check.endswith(")"):
            ErrorHandler.handle_error("Check syntax failed", "db", "critical")
            return False, ""
        return True, check

    @staticmethod
    def _validate_references(references: str) -> tuple[bool, str]:
        if not references.startswith("REFERENCES "):
            ErrorHandler.handle_error("References syntax failed", "db", "critical")
            return False, ""
        return True, references
