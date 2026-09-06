from datetime import UTC, datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer

from material_register.db.config.db_constants import DATABASE_NAME
from material_register.providers.paths_provider import PathsProvider
from material_register.providers.texts_provider import TextsProvider
from material_register.ui.helpers.formating_utils import format_datetime_to_locale
from material_register.workers.database_backup_worker import DatabaseBackupWorker

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.database_backup_widget import (
        DatabaseBackupWidget,
    )


class DatabaseBackupController(QObject):
    def __init__(self, database_backup_widget: "DatabaseBackupWidget", /) -> None:
        super().__init__()
        self.database_backup_widget = database_backup_widget
        self.main_window = self.database_backup_widget.right_toolbar_widget.main_window
        self.database_folder = PathsProvider.database
        self.database_path = (self.database_folder / DATABASE_NAME).with_suffix(".db")
        self.status_texts = TextsProvider.STATUS_TEXTS
        self.thread = None
        self.worker = None

    def setup_database_info_group(self) -> tuple[str, str, str]:
        database_stat = self.database_path.stat()
        name = self.database_path.name
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
        return name, size_text, last_modify

    def start_thread(self) -> None:
        self.main_window.status_bar.show_message("START_BACKUP")
        QTimer.singleShot(3000, self._start_worker)

    def _start_worker(self) -> None:
        self.thread = QThread()
        self.worker = DatabaseBackupWorker(self.database_folder)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._backup_error)
        self.worker.backup_created.connect(self._backup_created)
        self.worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self._thread_finished)
        self.thread.start()

    def _backup_error(self, key: str) -> None:
        self._show_result(key)

    def _backup_created(self, key: str) -> None:
        self._show_result(key)
        QTimer.singleShot(3000, self._show_ready)

    def _show_ready(self) -> None:
        self._show_result("READY")

    def _show_result(self, key: str) -> None:
        self.main_window.status_bar.show_message(key)

    def _thread_finished(self) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.worker = None
        self.thread = None
