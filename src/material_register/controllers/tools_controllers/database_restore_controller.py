from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer

from material_register.core.app_context import AppContext
from material_register.db.config.db_constants import DATABASE_NAME
from material_register.providers.lock_provider import LockProvider
from material_register.providers.paths_provider import PathsProvider
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.progress_dialog import ProgressDialog
from material_register.ui.setup.ui_texts import UiTexts
from material_register.utils.system import restart_application
from material_register.workers.tools_workers.database_restore_worker import (
    DatabaseRestoreWorker,
)

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.database_backup_widget import (
        DatabaseBackupWidget,
    )


class DatabaseRestoreController(QObject):
    def __init__(self, database_backup_widget: "DatabaseBackupWidget") -> None:
        super().__init__()
        self.database_backup_widget = database_backup_widget
        self.database_folder = PathsProvider.database
        self.database_path = (self.database_folder / DATABASE_NAME).with_suffix(".db")
        self.ui_texts = UiTexts.UI_TEXTS
        self.thread = None
        self.worker = None
        self.progress_dialog = None

    def start_restore_thread(self) -> None:
        restore_path = self.database_backup_widget.restore_path
        if restore_path is None:
            return
        self.database_folder.mkdir(parents=True, exist_ok=True)
        displayed_path = self.database_backup_widget.get_displayed_path(restore_path)
        question = MessageBoxes.show_question(
            self.database_backup_widget, "RESTORE_DATABASE", displayed_path
        )
        if not question:
            return
        self.progress_dialog = ProgressDialog(self.ui_texts, AppContext.MAIN_WINDOW)
        self.progress_dialog.set_label_text("restoreInProgressText")
        self.progress_dialog.show()
        QTimer.singleShot(
            0, lambda: self._start_worker(self.database_path, restore_path)
        )

    def _start_worker(self, database_path: Path, restore_path: Path) -> None:
        self.thread = QThread()
        self.worker = DatabaseRestoreWorker(database_path, restore_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._restore_error)
        self.worker.finished.connect(self._restore_finished)
        self.thread.start()

    def _restore_error(self, key: str) -> None:
        self._clean_thread()
        QTimer.singleShot(
            1000,
            lambda: self._finish_restore(key=key),
        )

    def _restore_finished(self) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, self._finish_restore)

    def _finish_restore(self, key: str | None = None) -> None:
        if key is None:
            self.progress_dialog.set_label_text("restartApplicationText")
            QTimer.singleShot(1000, self._restart_application)
            return
        ErrorDialog(self.database_backup_widget).show_dialog(key, False)
        self._reset_variables()

    def _restart_application(self) -> None:
        self.progress_dialog.close()
        LockProvider.unlock_app()
        restart_application("--database-restored")

    def _clean_thread(self) -> None:
        self.thread.quit()
        self.thread.wait()
        if self.worker:
            self.worker.deleteLater()
        self.thread.deleteLater()

    def _reset_variables(self) -> None:
        self.thread = None
        self.worker = None
        self.progress_dialog = None
