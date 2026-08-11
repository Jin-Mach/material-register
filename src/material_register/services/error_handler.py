from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from material_register.providers.logger_provider import LoggerProvider


class ErrorHandler:
    LEVELS = {"warning", "error", "critical"}
    loggers_map = {}
    ui_texts_error = ""

    @classmethod
    def init_handler(cls, logger_provider: type["LoggerProvider"]) -> None:
        cls.loggers_map = {
            "app": logger_provider.app,
            "ui": logger_provider.ui,
            "db": logger_provider.db,
            "export": logger_provider.export,
            "settings": logger_provider.settings,
            "error": logger_provider.error,
        }

    @classmethod
    def handle_error(
        cls, error: Exception | str, logger_name: str, level: str, exc_info: bool = True
    ) -> None:
        if not cls.loggers_map:
            return
        logger = cls.loggers_map.get(logger_name) or cls.loggers_map["error"]
        if level not in cls.LEVELS:
            level = "warning"
        if isinstance(error, Exception):
            logger.error(str(error), exc_info=exc_info)
        else:
            getattr(logger, level)(error)
