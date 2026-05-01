from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from material_register.providers.logger_provider import LoggerProvider


class ErrorHandler:
    LEVELS = {"warning", "error", "critical"}

    @classmethod
    def init_handler(cls, logger_provider: type["LoggerProvider"]) -> None:
        cls.loggers_map = {
            "app": logger_provider.app,
            "ui": logger_provider.ui,
            "db": logger_provider.db,
            "error": logger_provider.error
        }

    @classmethod
    def handle_error(cls, error: Exception | str, logger_name: str, level: str) -> None:
        if logger_name not in cls.loggers_map:
            logger_name = "error"
        logger = cls.loggers_map[logger_name]
        if level not in cls.LEVELS:
            level = "warning"
        if isinstance(error, Exception):
            logger.error(error, exc_info=True)
        else:
            getattr(logger, level)(error)