from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.providers.paths_provider import PathsProvider
from material_register.services.database_backup_service import DatabaseBackupService


class DatabaseBackupWorker(QObject):
    finished = Signal()
    backup_created = Signal()
    error = Signal(r)

    def __init__(self) -> None:
        super().__init__()
        self.database_path = PathsProvider.database
        self.backup_path = self.database_path / "backup"

    @Slot()
    def run(self) -> None:
        self.backup_path.mkdir(parents=True, exist_ok=True)
        year, month = DatabaseBackupWorker._find_missing_backup(
            self.backup_path, datetime.now(UTC)
        )
        if year is None and month is None:
            self.finished.emit()
            return
        if month is None:
            if not DatabaseBackupService.create_year_backup(self.database_path, year):
                self.error.emit()
                return
        else:
            if not DatabaseBackupService.create_month_backup(
                self.database_path, month, year
            ):
                self.error.emit()
                return
        self.backup_created.emit()
        self.finished.emit()

    @staticmethod
    def _find_missing_backup(
        backup_path: Path, current_date: datetime
    ) -> tuple[int | None, int | None]:
        current_year = current_date.year
        current_month = current_date.month
        if not any(backup_path.iterdir()):
            return current_year - 1, None
        previous_year = current_year - 1
        if not (
            backup_path / str(previous_year) / f"backup_{previous_year}.db"
        ).exists():
            return previous_year, None
        if current_month == 1:
            return None, None
        current_year_path = backup_path / str(current_year)
        month = f"{current_month - 1:02}"
        if not (current_year_path / f"{month}.db").exists():
            return current_year, current_month - 1
        return None, None
