import tomllib
from pathlib import Path

import tomli_w

from material_register.services.error_handler import ErrorHandler


class SettingsProvider:
    SETTINGS_PATH = None
    SETTINGS = {}

    @classmethod
    def provider_init(cls, resources_path: Path) -> None:
        cls.SETTINGS_PATH = resources_path / "config" / "settings.toml"
        cls.SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.SETTINGS = SettingsProvider._load_settings(cls.SETTINGS_PATH)

    @classmethod
    def save_settings(cls) -> bool:
        try:
            with open(cls.SETTINGS_PATH, "wb") as settings_file:
                tomli_w.dump(cls.SETTINGS, settings_file)
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "settings", "error")
            return False

    @classmethod
    def restore_settings(cls, section: str, sub_section: str) -> bool:
        try:
            settings = cls.SETTINGS.get(section, {}).get(sub_section, {})
            default = settings.get("default", {})
            user = settings.get("user", {})
            if not default or not user:
                return False
            for key, value in default.items():
                if key in user:
                    user[key] = value
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "settings", "error")
            return False

    @staticmethod
    def _load_settings(settings_path: Path) -> dict:
        try:
            if not settings_path.exists():
                return {}
            with open(settings_path, "rb") as settings_file:
                return tomllib.load(settings_file)
        except Exception as e:
            ErrorHandler.handle_error(e, "settings", "error")
            return {}
