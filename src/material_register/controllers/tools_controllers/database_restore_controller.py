from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer

from material_register.core.app_context import AppContext
from material_register.db.config.db_constants import DATABASE_NAME
from material_register.providers.lock_provider import LockProvider
from material_register.providers.paths_provider import PathsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_CRITICAL,
    LOGGER_DB,
)
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
        self._database_backup_widget = database_backup_widget
        self._database_folder = PathsProvider.database
        self._database_path = (self._database_folder / DATABASE_NAME).with_suffix(".db")
        self._ui_texts = UiTexts.UI_TEXTS
        self._thread = None
        self._worker = None
        self._progress_dialog = None

    def start_restore_thread(self) -> None:
        restore_path = self._database_backup_widget.restore_path
        if restore_path is None:
            return
        self._database_folder.mkdir(parents=True, exist_ok=True)
        displayed_path = self._database_backup_widget.get_displayed_path(restore_path)
        question = MessageBoxes.show_question(
            self._database_backup_widget, "RESTORE_DATABASE", displayed_path
        )
        if not question:
            return
        self._progress_dialog = ProgressDialog(self._ui_texts, AppContext.MAIN_WINDOW)
        self._progress_dialog.set_label_text("restoreInProgressText")
        self._progress_dialog.show()
        QTimer.singleShot(
            0, lambda: self._start_worker(self._database_path, restore_path)
        )

    def _start_worker(self, database_path: Path, restore_path: Path) -> None:
        self._thread = QThread()
        self._worker = DatabaseRestoreWorker(database_path, restore_path)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.error.connect(self._restore_error)
        self._worker.finished.connect(self._restore_finished)
        self._thread.start()

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
            self._progress_dialog.set_label_text("restartApplicationText")
            QTimer.singleShot(1000, self._restart_application)
            return
        self._progress_dialog.close()
        ErrorHandler.handle_error(
            f"{self.__class__.__name__}._finish_restore failed: {key}",
            LOGGER_DB,
            LOG_LEVEL_CRITICAL,
        )
        ErrorDialog(self._database_backup_widget).show_dialog("RESTORE_ERROR", False)
        self._reset_variables()

    def _restart_application(self) -> None:
        self._progress_dialog.close()
        LockProvider.unlock_app()
        restart_application("--database-restored")

    def _clean_thread(self) -> None:
        self._thread.quit()
        self._thread.wait()
        if self._worker:
            self._worker.deleteLater()
        self._thread.deleteLater()

    def _reset_variables(self) -> None:
        self._thread = None
        self._worker = None
        self._progress_dialog = None
