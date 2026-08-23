from PySide6.QtSql import QSqlDatabase

from material_register.db.config.db_constants import DATABASE_NAME
from material_register.db.create_connection import create_connection
from material_register.db.utils.schema_validator import is_schema_valid
from material_register.providers.paths_provider import PathsProvider
from material_register.services.error_handler import ErrorHandler


class DbInit:
    DATABASE_NAME = f"{DATABASE_NAME}.db"
    db_connection = None

    @classmethod
    def init_db(cls) -> tuple[bool, str]:
        try:
            cls.db_connection = create_connection(
                PathsProvider.database, cls.DATABASE_NAME, "main_connection"
            )
            if cls.db_connection is None:
                return False, "DATABASE_FAILED"
            schema_ok, schema_error = is_schema_valid(cls.db_connection)
            if not schema_ok:
                ErrorHandler.handle_error(schema_error, "db", "critical")
                return False, "DATABASE_FAILED"
            return True, ""
        except Exception as e:
            ErrorHandler.handle_error(e, "db", "critical")
            return False, "DATABASE_FAILED"

    @classmethod
    def thread_connection(
        cls, connection_name: str
    ) -> tuple[
        bool,
        str,
        QSqlDatabase | None,
    ]:
        thread_connection = create_connection(
            PathsProvider.database, cls.DATABASE_NAME, connection_name
        )
        if thread_connection is None:
            return False, "THREAD_CONNECTION_FAILED", None
        return True, "", thread_connection
