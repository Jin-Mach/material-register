import json

from pathlib import Path

from material_register.config.file_config import REQUIRED_JSON_FILES, REQUIRED_IMAGES, UI_KEYS, ERROR_KEYS, \
    HEADERS_KEYS, CONFIRM_KEYS
from material_register.services.error_handler import ErrorHandler


class FileProvider:

    @classmethod
    def check_missing_files(cls, resources_path: Path) -> set[Path]:
        invalid_files = set()
        texts_folder = cls._check_json_files(resources_path / "texts")
        invalid_files.update(texts_folder)
        images_folder = cls._check_images(resources_path / "images")
        invalid_files.update(images_folder)
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
        for file in REQUIRED_IMAGES:
            image_path = base_path / file
            if not image_path.exists():
                invalid_files.add(image_path)
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
            return False
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return False

    @classmethod
    def _check_ui_json(cls, data: dict[str, dict[str, str]]) -> bool:
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

    @classmethod
    def _check_confirm_json(cls, data: dict[str, str]) -> bool:
        for key in CONFIRM_KEYS:
            if key not in data:
                return False
            if not data[key]:
                return False
        return True