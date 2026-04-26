import requests

from pathlib import Path

from material_register.utils.network import is_internet_available
from material_register.utils.system import is_disk_writable


class DownloadProvider:
    FILES_MAP = {
        "texts/cs_CZ/ui_texts.json": "https://raw.githubusercontent.com/Jin-Mach/material-register/main/resources/texts/cs_CZ/ui_texts.json",
        "texts/en_GB/ui_texts.json": "https://raw.githubusercontent.com/Jin-Mach/material-register/main/resources/texts/en_GB/ui_texts.json",
    }

    FILES_SUFFIXES = [".json", ".qss"]
    ICONS_SUFFIXES = [".png", ".jpg", ".jpeg"]

    @classmethod
    def download_files(cls, invalid_files: set[Path], resource_path: Path) -> bool:
        try:
            for invalid_file in invalid_files:
                relative = invalid_file.relative_to(resource_path)
                url = cls.FILES_MAP.get(str(relative))
                if url:
                    if not cls._save_file(url, invalid_file):
                        return False
            return True
        except Exception as e:
            print(e)
            return False

    @classmethod
    def _save_file(cls, url: str, path: Path) -> bool:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix in cls.FILES_SUFFIXES:
                path.write_text(response.text)
            elif path.suffix in cls.ICONS_SUFFIXES:
                path.write_bytes(response.content)
            return True
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def is_ready_for_download(resource_path: Path) -> bool:
        return is_internet_available() and is_disk_writable(resource_path)