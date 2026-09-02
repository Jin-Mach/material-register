import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from material_register.services.error_handler import ErrorHandler


class SettingsProvider:
    DEFAULT_SETTINGS_PATH = None
    SETTINGS_PATH = None
    SETTINGS = {}

    @classmethod
    def provider_init(cls, resources_path: Path, config_path: Path) -> None:
        cls.DEFAULT_SETTINGS_PATH = resources_path / "config" / "settings.toml"
        cls.SETTINGS_PATH = config_path / "settings.toml"
        cls.SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        cls.SETTINGS = SettingsProvider._load_settings(cls.DEFAULT_SETTINGS_PATH)

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

    @classmethod
    def update_settings(cls) -> bool:
        try:
            default_settings = cls._load_settings(cls.DEFAULT_SETTINGS_PATH)
            user_settings = cls._load_settings(cls.SETTINGS_PATH)
            if not user_settings:
                cls.SETTINGS = default_settings
                return cls.save_settings()
            cls._update_settings_keys(default_settings, user_settings)
            cls.SETTINGS = user_settings
            return cls.save_settings()
        except Exception as e:
            ErrorHandler.handle_error(e, "settings", "error")
            return False

    @staticmethod
    def update_settings_sections(
        section: str, sub_section: str, values_items: list[str], default_value: int = 0
    ) -> None:
        default = {}
        for value in values_items:
            default[value] = default_value
        settings = SettingsProvider.SETTINGS.setdefault(section, {})
        cash_balance_values = settings.setdefault(sub_section, {})
        default_settings = cash_balance_values.setdefault("default", {})
        user_settings = cash_balance_values.setdefault("user", {})
        for current_settings in (default_settings, user_settings):
            current_keys = list(current_settings)
            for key in current_keys:
                if key not in default:
                    del current_settings[key]
            for key, value in default.items():
                key = str(key)
                if key not in current_settings:
                    current_settings[key] = value

    @classmethod
    def _update_settings_keys(
        cls, default: dict[str, Any], user: dict[str, Any]
    ) -> None:
        ignored_keys = ["cash_balance_values"]
        for key in list(user):
            if key not in default and key not in ignored_keys:
                del user[key]
        for key, default_value in default.items():
            if key not in user:
                user[key] = default_value
                continue
            if key in ignored_keys:
                continue
            user_value = user[key]
            if isinstance(default_value, dict) and isinstance(user_value, dict):
                if "default" in default_value and "user" in default_value:
                    cls._update_settings_keys(
                        default_value["default"], user_value["default"]
                    )
                    cls._update_settings_keys(default_value["user"], user_value["user"])
                else:
                    cls._update_settings_keys(default_value, user_value)

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
