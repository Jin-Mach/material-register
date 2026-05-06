from PySide6.QtCore import QLocale

from material_register.config.logging_congig import LOG_STRUCTURE
from material_register.db.create_connection import create_connection
from material_register.providers.logger_provider import LoggerProvider
from material_register.services.error_handler import ErrorHandler
from src.material_register.providers.language_provider import LanguageProvider
from src.material_register.providers.paths_provider import PathsProvider


class AppInit:

    @staticmethod
    def init_app() -> tuple[bool, str]:
        try:
            PathsProvider.paths_init(LOG_STRUCTURE)
            if PathsProvider.root is None or PathsProvider.logs is None:
                return False, "APP_INIT_FAILED"
            if not LoggerProvider.init_loggers(PathsProvider.logs, LOG_STRUCTURE):
                return False, "APP_INIT_FAILED"
            ErrorHandler.init_handler(LoggerProvider)
            if not create_connection(PathsProvider.database, "material-register.sqlite"):
                return False, "DATABASE_FAILED"
            LanguageProvider.language_init(QLocale().name())
            return True, ""
        except Exception as e:
            ErrorHandler.handle_error(e, "error", "critical")
            return False, "UNKNOWN_ERROR"