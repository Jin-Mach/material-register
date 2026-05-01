import json

from pathlib import Path

from material_register.services.error_handler import ErrorHandler


class TextsProvider:
    CURRENT_LANGUAGE = None
    RESOURCES_PATH = None
    UI_TEXTS = {}
    ERROR_TEXTS = {}

    @classmethod
    def provider_init(cls, language_code: str, resources_path: Path) -> None:
        cls.CURRENT_LANGUAGE = language_code
        cls.RESOURCES_PATH = resources_path
        cls.UI_TEXTS = cls._load_ui_texts(cls.RESOURCES_PATH)
        cls.ERROR_TEXTS = cls._load_error_texts(cls.RESOURCES_PATH)

    @classmethod
    def _load_ui_texts(cls, resources_path: Path) -> dict[str, dict[str, str]]:
        try:
            if not resources_path.exists():
                return {}
            file_path = resources_path / "texts" / cls.CURRENT_LANGUAGE / "ui_texts.json"
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return {}

    @classmethod
    def _load_error_texts(cls, resources_path: Path) -> dict[str, str]:
        try:
            if not resources_path.exists():
                return {}
            file_path = resources_path / "texts" / cls.CURRENT_LANGUAGE / "error_texts.json"
            return json.loads(file_path.read_text(encoding="utf-8"))
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return {}