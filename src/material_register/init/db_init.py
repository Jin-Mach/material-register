from material_register.db.config.db_constatns import DATABASE_NAME
from material_register.db.create_connection import create_connection
from material_register.providers.paths_provider import PathsProvider
from material_register.services.error_handler import ErrorHandler


class DbInit:
    DATABASE_NAME = f"{DATABASE_NAME}.db"
    db_connection = None

    @classmethod
    def init_db(cls) -> tuple[bool, str]:
        try:
            cls.db_connection = create_connection(PathsProvider.database, cls.DATABASE_NAME)
            if cls.db_connection is None:
                return False, "DATABASE_FAILED"
            return True, ""
        except Exception as e:
            ErrorHandler.handle_error(e, "db", "critical")
            return False, "DATABASE_FAILED"