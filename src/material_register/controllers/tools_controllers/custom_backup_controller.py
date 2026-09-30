from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer

from material_register.core.app_context import AppContext
from material_register.db.config.db_constants import DATABASE_NAME
from material_register.db.queries.tools_queries.database_backup_queries import (
    DatabaseBackupQueries,
)
from material_register.init.db_init import DbInit
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
        self._database_backup_widget = database_backup_widget
        self._database_folder = PathsProvider.database
        self._database_path = (self._database_folder / DATABASE_NAME).with_suffix(".db")
        self._ui_texts = UiTexts.UI_TEXTS
        self._notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("BACKUP", None)
        self._thread = None
        self._worker = None
        self._progress_dialog = None

    def start_backup_thread(self) -> None:
        if not DatabaseBackupQueries.has_data(DbInit.db_connection):
            question = MessageBoxes.show_question(
                self._database_backup_widget,
                "NO_CUSTOM_BACKUP_DATA",
            )
            if not question:
                return
        result = self._database_backup_widget.get_custom_backup_path()
        if result is None:
            return
        backup_path, displayed_path = result
        if backup_path.exists():
            question = MessageBoxes.show_question(
                self._database_backup_widget,
                "FILE_EXISTS",
                displayed_path,
            )
            if not question:
                return
        question = MessageBoxes.show_question(
            self._database_backup_widget,
            "CUSTOM_BACKUP",
            displayed_path,
        )
        if not question:
            return
        self._progress_dialog = ProgressDialog(
            self._ui_texts,
            AppContext.MAIN_WINDOW,
        )
        self._progress_dialog.set_label_text("backupInProgressText")
        self._progress_dialog.show()
        QTimer.singleShot(
            1000,
            lambda: self._start_worker(backup_path),
        )

    def _start_worker(self, backup_path: Path) -> None:
        self._thread = QThread()
        self._worker = CustomBackupWorker(
            self._database_path,
            backup_path,
        )
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.error.connect(self._backup_error)
        self._worker.finished.connect(self._backup_finished)
        self._thread.start()

    def _backup_error(self, key: str) -> None:
        self._clean_thread()
        self._finish_backup(key=key)

    def _backup_finished(self) -> None:
        self._clean_thread()
        self._finish_backup()

    def _finish_backup(self, key: str | None = None) -> None:
        self._progress_dialog.close()
        if key is None:
            CustomBackupController._notification_handler(
                self._notification_texts,
                "BACKUP_CREATED",
                "Backup created",
            )
            self._reset_variables()
            return
        ErrorDialog(self._database_backup_widget).show_dialog(key, False)
        self._reset_variables()

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
