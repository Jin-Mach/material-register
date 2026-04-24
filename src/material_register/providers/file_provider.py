import json

from pathlib import Path


class FileProvider:

    REQUIRED_FILES = [
        Path("cs_CZ/ui_texts.json"),
        Path("en_GB/ui_texts.json"),
    ]

    REQUIRED_KEYS = [
        ("MainWindow", "titleText"),
        ("SidePanel", "registerButtonText"),
        ("SidePanel", "registerButtonTooltipText"),
        ("ActionsWidget", "addActionButtonTooltipText"),
        ("ActionsWidget", "deleteActionButtonTooltipText"),
    ]

    @classmethod
    def check_missing_files(cls, resources_path: Path) -> set[Path]:
        invalid_files = set()
        texts_files = cls._check_texts_files(resources_path / "texts")
        if texts_files:
            invalid_files.update(texts_files)
        return invalid_files

    @classmethod
    def _check_texts_files(cls, text_path: Path) -> set[Path]:
        invalid_files = set()
        for path in cls.REQUIRED_FILES:
            file_path = text_path / path
            if not file_path.exists():
                invalid_files.add(file_path)
                continue
            if not cls._is_file_valid(file_path):
                invalid_files.add(file_path)
        return invalid_files

    @classmethod
    def _is_file_valid(cls, file: Path) -> bool:
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            for section, key in cls.REQUIRED_KEYS:
                if section not in data:
                    return False
                if key not in data[section]:
                    return False
                value = data[section][key]
                if value is None or value == "":
                    return False
            return True
        except Exception as e:
            print(e)
            return False