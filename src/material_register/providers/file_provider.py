import json
from pathlib import Path


class FileProvider:
    REQUIRED_FILES = [
        Path("cs_CZ/ui_texts.json"),
        Path("en_GB/ui_texts.json"),
        Path("cs_CZ/error_texts.json"),
        Path("en_GB/error_texts.json"),
    ]

    UI_KEYS = [
        ("MainWindow", "titleText"),
        ("SidePanel", "registerButtonText"),
        ("SidePanel", "registerButtonTooltipText"),
        ("ActionsWidget", "addActionButtonTooltipText"),
        ("ActionsWidget", "deleteActionButtonTooltipText"),
        ("ErrorDialog", "closeDialogButtonText"),
        ("ErrorDialog", "closeDialogButtonTooltipText"),
        ("ErrorDialog", "closeAppButtonText"),
        ("ErrorDialog", "closeAppButtonTooltipText"),
    ]

    ERROR_KEYS = [
        "APP_INIT_FAILED",
        "RESOURCES_MISSING",
        "DOWNLOAD_FAILED",
        "TEXTS_LOAD_FAILED",
        "CRITICAL_FAILURE",
        "UNKNOWN_ERROR",
    ]

    @classmethod
    def check_missing_files(cls, resources_path: Path) -> set[Path]:
        invalid_files = set()
        texts_files = cls._check_json_files(resources_path / "texts")
        errors_files = cls._check_json_files(resources_path / "errors")
        invalid_files.update(texts_files)
        invalid_files.update(errors_files)
        return invalid_files

    @classmethod
    def _check_json_files(cls, base_path: Path) -> set[Path]:
        invalid_files = set()
        for path in cls.REQUIRED_FILES:
            file_path = base_path / path
            if not file_path.exists():
                invalid_files.add(file_path)
                continue
            if not cls._is_file_valid(file_path):
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
            return False
        except Exception as e:
            print(e)
            return False

    @classmethod
    def _check_ui_json(cls, data: dict[str, dict[str, str]]) -> bool:
        for section, key in cls.UI_KEYS:
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
        for key in cls.ERROR_KEYS:
            if key not in data:
                return False
            if not data[key]:
                return False
        return True