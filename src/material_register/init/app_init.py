from PySide6.QtCore import QLocale

from material_register.config.logging_config import LOG_STRUCTURE
from material_register.providers.language_provider import LanguageProvider
from material_register.providers.logger_provider import LoggerProvider
from material_register.providers.paths_provider import PathsProvider
from material_register.services.error_handler import ErrorHandler


class AppInit:

    @staticmethod
    def init_app() -> tuple[bool, str]:
        try:
            PathsProvider.paths_init(LOG_STRUCTURE)
            if any([PathsProvider.root is None, PathsProvider.resources is None,
                    PathsProvider.database is None, PathsProvider.logs is None]):
                return False, "APP_INIT_FAILED"
            if not LoggerProvider.init_loggers(PathsProvider.logs, LOG_STRUCTURE):
                return False, "APP_INIT_FAILED"
            ErrorHandler.init_handler(LoggerProvider)
            LanguageProvider.language_init(QLocale().name())
            return True, ""
        except Exception as e:
            ErrorHandler.handle_error(e, "error", "critical")
            return False, "UNKNOWN_ERROR"