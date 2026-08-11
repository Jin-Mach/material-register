import json
from pathlib import Path

from material_register.services.error_handler import ErrorHandler


class TextsProvider:
    CURRENT_LANGUAGE = None
    RESOURCES_PATH = None
    UI_TEXTS = {}
    HEADERS_TEXTS = {}
    CONFIRM_TEXTS = {}
    NOTIFICATION_TEXTS = {}
    ERROR_TEXTS = {}
    STATUS_TEXTS = {}
    EXPORT_TEXTS = {}

    @classmethod
    def provider_init(cls, language_code: str, resources_path: Path) -> None:
        cls.CURRENT_LANGUAGE = language_code
        cls.RESOURCES_PATH = resources_path
        cls.UI_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "ui_texts.json")
        cls.HEADERS_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "headers_texts.json")
        cls.ERROR_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "error_texts.json")
        cls.CONFIRM_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "confirm_texts.json")
        cls.NOTIFICATION_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "notification_texts.json")
        cls.STATUS_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "status_texts.json")
        cls.EXPORT_TEXTS = cls._load_texts(cls.RESOURCES_PATH, "export_texts.json")

    @classmethod
    def _load_texts(cls, resources_path: Path, json_file: str) -> dict[str, dict[str, str]]:
        try:
            if not resources_path.exists():
                return {}
            file_path = resources_path / "texts" / cls.CURRENT_LANGUAGE / json_file
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return {}