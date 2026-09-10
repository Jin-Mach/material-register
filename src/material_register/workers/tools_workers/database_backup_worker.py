from datetime import UTC, datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot

from material_register.db.config.db_constants import DATABASE_NAME
from material_register.services.database_backup_service import DatabaseBackupService


class DatabaseBackupWorker(QObject):
    finished = Signal()
    backup_created = Signal(str)
    error = Signal(str)

    def __init__(self, database_folder: Path) -> None:
        super().__init__()
        self.database_folder = database_folder
        self.backup_folder = self.database_folder / "backup"
        self.database_path = Path(self.database_folder / DATABASE_NAME).with_suffix(
            ".db"
        )

    @Slot()
    def run(self) -> None:
        self.backup_folder.mkdir(parents=True, exist_ok=True)
        year, month = DatabaseBackupWorker._find_missing_backup(
            self.backup_folder, datetime.now(UTC)
        )
        if year is None and month is None:
            self.finished.emit()
            return
        if month is None:
            if not DatabaseBackupService.create_year_backup(self.database_path, year):
                self.error.emit("BACKUP_FAILED")
                self.finished.emit()
                return
        else:
            if not DatabaseBackupService.create_month_backup(
                self.database_path, month, year
            ):
                self.error.emit("BACKUP_FAILED")
                self.finished.emit()
                return
        self.backup_created.emit("BACKUP_CREATED")
        self.finished.emit()

    @staticmethod
    def _find_missing_backup(
        backup_folder: Path, current_date: datetime
    ) -> tuple[int | None, int | None]:
        current_year = current_date.year
        current_month = current_date.month
        if not any(backup_folder.iterdir()):
            return current_year - 1, None
        previous_year = current_year - 1
        if not (
            backup_folder / str(previous_year) / f"backup_{previous_year}.db"
        ).exists():
            return previous_year, None
        if current_month == 1:
            return None, None
        current_year_path = backup_folder / str(current_year)
        month = f"{current_month - 1:02}"
        if not (current_year_path / f"{month}.db").exists():
            return current_year, current_month - 1
        return None, None
