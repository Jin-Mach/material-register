import logging

from pathlib import Path
from logging.handlers import RotatingFileHandler


class LoggerProvider:
    LOGS_PATH = None
    LOG_STRUCTURE = {}
    FORMATTER = None

    @classmethod
    def init_loggers(cls, logs_path: Path, log_structure: dict[str, tuple[str, str]]) -> None:
        cls.LOGS_PATH = logs_path
        cls.LOG_STRUCTURE = log_structure
        cls.FORMATTER = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s"
        )
        cls.app = cls._create_logger("material-register.app", "app")
        cls.ui = cls._create_logger("material-register.ui", "ui")
        cls.db = cls._create_logger("material-register.db", "db")
        cls.error = cls._create_logger("material-register.error","error")

    @classmethod
    def _create_logger(cls, name: str, key: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(logging.WARNING)
        logger.propagate = False
        folder, file_name = cls.LOG_STRUCTURE[key]
        path = cls.LOGS_PATH / folder / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        if logger.handlers:
            return logger
        handler = RotatingFileHandler(path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
        handler.setFormatter(cls.FORMATTER)
        logger.addHandler(handler)
        return logger