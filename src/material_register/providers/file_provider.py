import json
import tomllib
from pathlib import Path

from material_register.config.file_config import (
    CONFIRM_STRUCTURE,
    ERROR_KEYS,
    EXPORT_KEYS,
    HEADERS_KEYS,
    NOTIFICATION_KEYS,
    REQUIRED_CONFIG_FILES,
    REQUIRED_IMAGES,
    REQUIRED_JSON_FILES,
    REQUIRED_STYLES_FILES,
    STATUS_KEYS,
    UI_KEYS,
)
from material_register.services.error_handler import ErrorHandler


class FileProvider:
    @classmethod
    def check_missing_files(cls, resources_path: Path) -> set[Path]:
        invalid_files = set()
        texts_folder = cls._check_json_files(resources_path / "texts")
        invalid_files.update(texts_folder)
        images_folder = cls._check_images(resources_path / "images")
        invalid_files.update(images_folder)
        config_files = cls._check_config_files(resources_path)
        invalid_files.update(config_files)
        style_files = cls._check_style_files(resources_path / "styles")
        invalid_files.update(style_files)
        return invalid_files

    @classmethod
    def _check_json_files(cls, base_path: Path) -> set[Path]:
        invalid_files = set()
        for path in REQUIRED_JSON_FILES:
            file_path = base_path / path
            if not file_path.exists():
                invalid_files.add(file_path)
                continue
            if not cls._is_file_valid(file_path):
                invalid_files.add(file_path)
        return invalid_files

    @classmethod
    def _check_images(cls, base_path: Path) -> set[Path]:
        invalid_files = set()
        for path in REQUIRED_IMAGES:
            image_path = base_path / path
            if not image_path.exists():
                invalid_files.add(image_path)
        return invalid_files

    @classmethod
    def _check_config_files(cls, base_path: Path) -> set[Path]:
        invalid_files = set()
        for path in REQUIRED_CONFIG_FILES:
            file_path = base_path / path
            if not file_path.exists():
                invalid_files.add(file_path)
                continue
            if not cls._is_toml_valid(file_path):
                invalid_files.add(file_path)
        return invalid_files

    @classmethod
    def _check_style_files(cls, base_path: Path) -> set[Path]:
        invalid_files = set()
        for path in REQUIRED_STYLES_FILES:
            file_path = base_path / path
            if not file_path.exists():
                invalid_files.add(file_path)
                continue
            if not cls._is_qss_valid(file_path):
                invalid_files.add(file_path)
        return invalid_files

    @classmethod
    def _is_file_valid(cls, file: Path) -> bool:
        try:
            name = file.stem
            data = json.loads(file.read_text(encoding="utf-8"))
            if name == "ui_texts":
                return cls._check_ui_json(data)
            if name == "error_texts":
                return cls._check_error_json(data)
            if name == "headers_texts":
                return cls._check_headers_json(data)
            if name == "confirm_texts":
                return cls._check_confirm_json(data)
            if name == "notification_texts":
                return cls._check_notification_json(data)
            if name == "status_texts":
                return cls._check_status_json(data)
            if name == "export_texts":
                return cls._check_export_json(data)
            return False
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return False

    @staticmethod
    def _is_toml_valid(file: Path) -> bool:
        try:
            with open(file, "rb") as settings_file:
                tomllib.load(settings_file)
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return False

    @staticmethod
    def _is_qss_valid(file: Path) -> bool:
        try:
            return bool(file.read_text(encoding="utf-8").strip())
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return False

    @classmethod
    def _check_ui_json(cls, data: dict[str, dict[str, str | list[str]]]) -> bool:
        for section, key in UI_KEYS:
            if section not in data:
                return False
            if key not in data[section]:
                return False
            value = data[section][key]
            if value is None or value == "":
                return False
        return True

    @classmethod
    def _check_error_json(cls, data: dict[str, str]) -> bool:
        for key in ERROR_KEYS:
            if key not in data:
                return False
            if not data[key]:
                return False
        return True

    @classmethod
    def _check_headers_json(cls, data: dict[str, dict[str, str]]) -> bool:
        for section, key in HEADERS_KEYS:
            if section not in data:
                return False
            if key not in data[section]:
                return False
            value = data[section][key]
            if value is None or value == "":
                return False
        return True

    @staticmethod
    def _check_confirm_json(data: dict[str, dict[str, str]]) -> bool:
        for section, keys in CONFIRM_STRUCTURE.items():
            if section not in data:
                return False
            for key in keys:
                if key not in data[section]:
                    return False
                if not data[section][key]:
                    return False
        return True

    @staticmethod
    def _check_notification_json(data: dict[str, dict[str, str]]) -> bool:
        for section, key in NOTIFICATION_KEYS:
            if section not in data:
                return False
            if key not in data[section]:
                return False
            if not data[section][key]:
                return False
        return True

    @classmethod
    def _check_status_json(cls, data: dict[str, dict[str, str]]) -> bool:
        for key in STATUS_KEYS:
            if key not in data:
                return False
            if not data[key]:
                return False
        return True

    @classmethod
    def _check_export_json(cls, data: dict[str, dict[str, str]]) -> bool:
        for section, key in EXPORT_KEYS:
            if section not in data:
                return False
            if key not in data[section]:
                return False
            value = data[section][key]
            if value is None or value == "":
                return False
        return True
