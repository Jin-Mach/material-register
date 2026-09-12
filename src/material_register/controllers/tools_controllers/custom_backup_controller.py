from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer

from material_register.core.app_context import AppContext
from material_register.db.config.db_constants import DATABASE_NAME
from material_register.providers.paths_provider import PathsProvider
from material_register.providers.texts_provider import TextsProvider
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.notification_dialog import NotificationDialog
from material_register.ui.dialogs.progress_dialog import ProgressDialog
from material_register.ui.setup.ui_texts import UiTexts
from material_register.workers.tools_workers.custom_backup_worker import (
    CustomBackupWorker,
)

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.database_backup_widget import (
        DatabaseBackupWidget,
    )


class CustomBackupController(QObject):
    def __init__(self, database_backup_widget: "DatabaseBackupWidget", /) -> None:
        super().__init__()
        self.database_backup_widget = database_backup_widget
        self.database_folder = PathsProvider.database
        self.database_path = (self.database_folder / DATABASE_NAME).with_suffix(".db")
        self.ui_texts = UiTexts.UI_TEXTS
        self.notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("BACKUP", None)
        self.thread = None
        self.worker = None
        self.progress_dialog = None

    def start_backup_thread(self) -> None:
        result = self.database_backup_widget.get_custom_backup_path()
        if result is None:
            return
        backup_path, displayed_path = result
        if backup_path.exists():
            question = MessageBoxes.show_question(
                self.database_backup_widget,
                "FILE_EXISTS",
                displayed_path,
            )
            if not question:
                return
        question = MessageBoxes.show_question(
            self.database_backup_widget,
            "CUSTOM_BACKUP",
            displayed_path,
        )
        if not question:
            return
        self.progress_dialog = ProgressDialog(
            self.ui_texts,
            AppContext.MAIN_WINDOW,
        )
        self.progress_dialog.set_label_text("backupInProgressText")
        self.progress_dialog.show()
        QTimer.singleShot(
            1000,
            lambda: self._start_worker(backup_path),
        )

    def _start_worker(self, backup_path: Path) -> None:
        self.thread = QThread()
        self.worker = CustomBackupWorker(
            self.database_path,
            backup_path,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._backup_error)
        self.worker.finished.connect(self._backup_finished)
        self.thread.start()

    def _backup_error(self, key: str) -> None:
        self._clean_thread()
        self._finish_backup(key=key)

    def _backup_finished(self) -> None:
        self._clean_thread()
        self._finish_backup()

    def _finish_backup(self, key: str | None = None) -> None:
        self.progress_dialog.close()
        if key is None:
            CustomBackupController._notification_handler(
                self.notification_texts,
                "BACKUP_CREATED",
                "Backup created",
            )
            self._reset_variables()
            return
        ErrorDialog(self.database_backup_widget).show_dialog(key, False)
        self._reset_variables()

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

    @staticmethod
    def _notification_handler(
        notification_texts: dict[str, str] | None,
        key: str,
        default: str,
    ) -> None:
        if notification_texts is None:
            return
        notification = NotificationDialog(
            AppContext.MAIN_WINDOW,
            notification_texts.get(key, default),
        )
        notification.show_notification()
