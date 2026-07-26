import tomllib

from pathlib import Path

from material_register.services.error_handler import ErrorHandler


class SettingsProvider:
    SETTINGS_PATH = None
    SETTINGS = {}

    @classmethod
    def provider_init(cls, resources_path: Path) -> None:
        cls.SETTINGS_PATH = resources_path / "config" / "settings.toml"
        cls.SETTINGS = cls._load_settings(cls.SETTINGS_PATH)

    @classmethod
    def _load_settings(cls, settings_path: Path) -> dict:
        try:
            if not settings_path.exists():
                return {}
            with open(settings_path, "rb") as settings_file:
                cls.SETTINGS = tomllib.load(settings_file)
            return cls.SETTINGS
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return {}