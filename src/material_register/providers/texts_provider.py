import json
from pathlib import Path

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_ERROR,
    LOGGER_APP,
)


class TextsProvider:
    CURRENT_LANGUAGE: str | None = None
    RESOURCES_PATH: Path | None = None
    UI_TEXTS: dict[str, dict[str, str]] = {}
    HEADERS_TEXTS: dict[str, dict[str, str]] = {}
    CONFIRM_TEXTS: dict[str, dict[str, str]] = {}
    NOTIFICATION_TEXTS: dict[str, dict[str, str]] = {}
    ERROR_TEXTS: dict[str, dict[str, str]] = {}
    STATUS_TEXTS: dict[str, dict[str, str]] = {}
    EXPORT_TEXTS: dict[str, dict[str, str]] = {}

    @classmethod
    def provider_init(cls, language_code: str, resources_path: Path) -> None:
        cls.CURRENT_LANGUAGE = language_code
        cls.RESOURCES_PATH = resources_path
        cls.UI_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "ui_texts.json")
        cls.HEADERS_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "headers_texts.json")
        cls.ERROR_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "error_texts.json")
        cls.CONFIRM_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "confirm_texts.json")
        cls.NOTIFICATION_TEXTS = cls._load_texts(
            cls.RESOURCES_PATH, "notification_texts.json"
        )
        cls.STATUS_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "status_texts.json")
        cls.EXPORT_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "export_texts.json")

    @classmethod
    def _load_texts(
        cls, resources_path: Path, json_file: str
    ) -> dict[str, dict[str, str]]:
        try:
            if not resources_path.exists():
                return {}
            file_path = resources_path / "texts" / cls.CURRENT_LANGUAGE / json_file
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            ErrorHandler.handle_error(e, LOGGER_APP, LOG_LEVEL_ERROR)
            return {}
