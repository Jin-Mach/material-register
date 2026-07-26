import requests

from pathlib import Path

from material_register.config.download_config import FILES_MAP, ICONS_MAP, FILES_SUFFIXES, ICONS_SUFFIXES
from material_register.services.error_handler import ErrorHandler
from material_register.utils.network import is_internet_available
from material_register.utils.system import is_disk_writable


class DownloadProvider:

    @classmethod
    def download_files(cls, invalid_files: set[Path], resource_path: Path) -> bool:
        try:
            for invalid_file in invalid_files:
                relative = invalid_file.relative_to(resource_path)
                url = FILES_MAP.get(str(relative)) or ICONS_MAP.get(str(relative))
                if url:
                    if not cls._save_file(url, invalid_file):
                        return False
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return False

    @classmethod
    def _save_file(cls, url: str, path: Path) -> bool:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix in FILES_SUFFIXES:
                path.write_text(response.text, encoding="utf-8")
            elif path.suffix in ICONS_SUFFIXES:
                path.write_bytes(response.content)
            else:
                return False
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return False

    @staticmethod
    def is_ready_for_download(resource_path: Path) -> dict[str, bool]:
        return {"internet": is_internet_available(),
                "writable": is_disk_writable(resource_path)}