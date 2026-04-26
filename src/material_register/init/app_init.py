from PySide6.QtCore import QLocale

from material_register.config.logging_congig import LOG_STRUCTURE
from material_register.providers.logger_provider import LoggerProvider
from material_register.services.error_handler import ErrorHandler
from src.material_register.providers.language_provider import LanguageProvider
from src.material_register.providers.paths_provider import PathsProvider


class AppInit:

    @staticmethod
    def init_app() -> bool:
        try:
            PathsProvider.paths_init(LOG_STRUCTURE)
            if PathsProvider.root is None:
                return False
            if PathsProvider.logs is None:
                return False
            LoggerProvider.init_loggers(PathsProvider.logs, LOG_STRUCTURE)
            ErrorHandler.init_handler(LoggerProvider)
            LanguageProvider.language_init(QLocale().name())
            return True
        except Exception as e:
            print(e)
            return False