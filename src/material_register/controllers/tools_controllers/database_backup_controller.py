from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer

from material_register.db.config.db_constants import DATABASE_NAME
from material_register.providers.paths_provider import PathsProvider
from material_register.services.database_backup_service import DatabaseBackupService
from material_register.utils.formatting_utils import format_datetime_to_locale
from material_register.workers.tools_workers.database_backup_worker import (
    DatabaseBackupWorker,
)

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.database_backup_widget import (
        DatabaseBackupWidget,
    )


class DatabaseBackupController(QObject):
    def __init__(self, database_backup_widget: "DatabaseBackupWidget", /) -> None:
        super().__init__()
        self._database_backup_widget = database_backup_widget
        self._main_window = (
            self._database_backup_widget.right_toolbar_widget.main_window
        )
        self._database_folder = PathsProvider.database
        self._database_path = (self._database_folder / DATABASE_NAME).with_suffix(".db")
        self._backup_path = self._database_folder / "backup"
        self._thread = None
        self._worker = None

    def setup_database_info_group(self) -> tuple[str, str, str, str]:
        database_stat = self._database_path.stat()
        name = self._database_path.name
        size = int(database_stat.st_size)
        if size < 1024 * 1024:
            size_text = f"{size / 1024:.1f} KB"
        else:
            size_text = f"{size / (1024**2):.1f} MB"
        last_modify = format_datetime_to_locale(
            datetime.fromtimestamp(database_stat.st_mtime, UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        last_backup = DatabaseBackupService.get_last_backup_date(
            self._database_folder / "backup"
        )
        last_backup_text = (
            format_datetime_to_locale(last_backup.strftime("%Y-%m-%d %H:%M:%S"))
            if last_backup
            else "?"
        )
        return name, size_text, last_modify, last_backup_text

    def get_backup_map(self) -> dict[str, list[Path]]:
        self._backup_path.mkdir(parents=True, exist_ok=True)
        backup_map = DatabaseBackupService.get_backup_tree(self._backup_path)
        return backup_map

    def start_thread(self) -> None:
        self._main_window.status_bar.show_message("START_BACKUP")
        QTimer.singleShot(3000, self._start_worker)

    def _start_worker(self) -> None:
        self._thread = QThread()
        self._worker = DatabaseBackupWorker(self._database_folder)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.error.connect(self._backup_error)
        self._worker.backup_created.connect(self._backup_created)
        self._worker.finished.connect(self._thread_finished)
        self._thread.start()

    def _backup_error(self, key: str) -> None:
        self._show_result(key)

    def _backup_created(self, key: str) -> None:
        self._show_result(key)
        QTimer.singleShot(3000, self._show_ready)

    def _show_ready(self) -> None:
        self._show_result("READY")

    def _show_result(self, key: str) -> None:
        self._database_backup_widget.setup_info_group()
        self._database_backup_widget.setup_backup_tree()
        self._main_window.status_bar.show_message(key)

    def _thread_finished(self) -> None:
        self._clean_thread()

    def _clean_thread(self) -> None:
        self._thread.quit()
        self._thread.wait()
        if self._worker:
            self._worker.deleteLater()
        self._thread.deleteLater()
        self._reset_variables()

    def _reset_variables(self) -> None:
        self._thread = None
        self._worker = None
