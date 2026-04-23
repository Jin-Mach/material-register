import json

from pathlib import Path


class TextsProvider:
    CURRENT_LANGUAGE = None
    RESOURCES_PATH = None
    UI_TEXTS = {}

    @classmethod
    def provider_init(cls, language_code: str, resources_path: Path) -> None:
        cls.CURRENT_LANGUAGE = language_code
        cls.RESOURCES_PATH = resources_path
        cls.UI_TEXTS = cls._load_ui_texts(cls.RESOURCES_PATH)

    @classmethod
    def _load_ui_texts(cls, resources_path: Path) -> dict[str, dict[str, str]]:
        try:
            if not resources_path.exists():
                return {}
            with open(resources_path / "texts" / cls.CURRENT_LANGUAGE / "ui_texts.json", "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(e)
            return {}
