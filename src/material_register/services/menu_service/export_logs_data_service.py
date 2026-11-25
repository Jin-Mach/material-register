import zipfile
from pathlib import Path


class ExportLogsDataService:
    @staticmethod
    def create_zip_file(from_path: Path, to_path: Path) -> tuple[bool, str]:
        try:
            with zipfile.ZipFile(to_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file in from_path.rglob("*"):
                    if file.is_file() and file.resolve() != to_path.resolve():
                        zip_file.write(file, file.relative_to(from_path))
            return True, ""
        except Exception as e:
            to_path.unlink(missing_ok=True)
            return False, str(e)
