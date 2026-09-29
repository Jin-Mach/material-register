from typing import TYPE_CHECKING

from material_register.ui.config.ui_constants import (
    LOG_LEVEL_CRITICAL,
    LOG_LEVEL_ERROR,
    LOG_LEVEL_WARNING,
    LOGGER_APP,
    LOGGER_DB,
    LOGGER_ERROR,
    LOGGER_EXPORT,
    LOGGER_SETTINGS,
    LOGGER_UI,
)

if TYPE_CHECKING:
    from material_register.providers.logger_provider import LoggerProvider


class ErrorHandler:
    LEVELS = {
        LOG_LEVEL_WARNING,
        LOG_LEVEL_ERROR,
        LOG_LEVEL_CRITICAL,
    }
    loggers_map = {}
    ui_texts_error = ""

    @classmethod
    def init_handler(cls, logger_provider: type["LoggerProvider"]) -> None:
        cls.loggers_map = {
            LOGGER_APP: logger_provider.app,
            LOGGER_UI: logger_provider.ui,
            LOGGER_DB: logger_provider.db,
            LOGGER_EXPORT: logger_provider.export,
            LOGGER_SETTINGS: logger_provider.settings,
            LOGGER_ERROR: logger_provider.error,
        }

    @classmethod
    def handle_error(
        cls, error: Exception | str, logger_name: str, level: str, exc_info: bool = True
    ) -> None:
        if not cls.loggers_map:
            return
        logger = cls.loggers_map.get(logger_name) or cls.loggers_map[LOGGER_ERROR]
        if level not in cls.LEVELS:
            level = LOG_LEVEL_WARNING
        if isinstance(error, Exception):
            logger.error(str(error), exc_info=exc_info)
        else:
            getattr(logger, level)(error)
