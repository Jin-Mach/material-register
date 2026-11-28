from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QStandardPaths, QThread, QTimer
from PySide6.QtWidgets import QFileDialog, QWidget

from material_register.core.app_context import AppContext
from material_register.providers.paths_provider import PathsProvider
from material_register.providers.texts_provider import TextsProvider
from material_register.services.database_backup_service import DatabaseBackupService
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_WARNING, LOGGER_DB
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.notification_dialog import NotificationDialog
from material_register.ui.dialogs.progress_dialog import ProgressDialog
from material_register.ui.setup.ui_texts import UiTexts
from material_register.workers.menu_workers.database_backup_check_worker import (
    DatabaseBackupCheckWorker,
)

if TYPE_CHECKING:
    from material_register.ui.widgets.menu_bar import MenuBar


class DatabaseBackupCheckController(QObject):
    def __init__(self, menu_bar: "MenuBar") -> None:
        super().__init__(menu_bar)
        self.menu_bar = menu_bar
        self.ui_texts = UiTexts.UI_TEXTS
        self.notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("CHECKS", None)
        self.custom_check = None
        self.progress_dialog = None
        self.worker = None
        self.thread = None

    def start_check(self, custom_check: bool) -> None:
        self.custom_check = custom_check
        check_path = PathsProvider.database / "backup"
        if self.custom_check:
            menu_texts = self.ui_texts.get(self.menu_bar.__class__.__name__, {})
            filter_text = menu_texts.get("fileCheckDialogFilterText", "Database files")
            file_path, _ = QFileDialog.getOpenFileName(
                AppContext.MAIN_WINDOW,
                menu_texts.get("fileCheckDialogTitleText", "Select database backup"),
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.HomeLocation
                ),
                f"{filter_text} (*.db)",
            )
            if not file_path:
                return
            check_path = Path(file_path)
        if not check_path.exists():
            return
        self.progress_dialog = ProgressDialog(self.ui_texts, AppContext.MAIN_WINDOW)
        self.progress_dialog.set_label_text("checkInProgressText")
        self.progress_dialog.show()
        self._start_worker(check_path)

    def _start_worker(self, check_path: Path) -> None:
        if self.thread is not None or self.worker is not None:
            return
        self.thread = QThread()
        self.worker = DatabaseBackupCheckWorker(check_path, self.custom_check)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._check_ok)
        self.worker.empty.connect(self._check_empty)
        self.worker.invalid.connect(self._check_invalid)
        self.worker.error.connect(self._check_error)
        self.thread.start()

    def _check_error(self, error: str) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, lambda: self._finish_check(error=error))

    def _check_empty(self) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, lambda: self._finish_check(empty=True))

    def _check_invalid(self, invalid_files: list[Path], check_errors: str) -> None:
        self._clean_thread()
        QTimer.singleShot(
            1000,
            lambda: self._finish_check(
                invalid_files=invalid_files, check_errors=check_errors
            ),
        )

    def _check_ok(self) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, self._finish_check)

    def _clean_thread(self) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _reset_variables(self) -> None:
        self.progress_dialog = None
        self.worker = None
        self.thread = None

    def _finish_check(
        self,
        empty: bool = False,
        invalid_files: list[Path] | None = None,
        check_errors: str = "",
        error: str | None = None,
    ) -> None:
        self.progress_dialog.close()
        self._reset_variables()
        if error is not None:
            DatabaseBackupCheckController._handle_check_error(
                error,
                f"{self.__class__.__name__}._database_backup_check_error",
                AppContext.MAIN_WINDOW,
            )
            self.custom_check = None
            return
        if empty:
            MessageBoxes.show_error(AppContext.MAIN_WINDOW, "NO_DATABASE_BACKUP")
            self.custom_check = None
            return
        if invalid_files is not None:
            if not check_errors:
                check_errors = f"Invalid files count: {len(invalid_files)}"
            ErrorHandler.handle_error(check_errors, LOGGER_DB, LOG_LEVEL_WARNING)
            if self.custom_check:
                MessageBoxes.show_error(AppContext.MAIN_WINDOW, "INVALID_CUSTOM_BACKUP")
            else:
                question = MessageBoxes.show_question(
                    AppContext.MAIN_WINDOW, "DELETE_INVALID_BACKUP"
                )
                if question:
                    if not DatabaseBackupService.delete_invalid_backup(invalid_files):
                        DatabaseBackupCheckController._handle_check_error(
                            "Remove invalid backup failed",
                            f"{self.__class__.__name__}._database_backup_check_error",
                            AppContext.MAIN_WINDOW,
                        )
                    else:
                        DatabaseBackupCheckController._notification_handler(
                            self.notification_texts,
                            "BACKUP_DELETED",
                            "Invalid backups deleted",
                        )
            self.custom_check = None
            return
        DatabaseBackupCheckController._notification_handler(
            self.notification_texts, "BACKUP_CHECK", "Backup check completed"
        )
        self.custom_check = None

    @staticmethod
    def _handle_check_error(
        error: str, method: str, parent: QWidget, error_key: str = "DATABASE_ERROR"
    ) -> None:
        if not error:
            error = f"Unknown export error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", LOGGER_DB, LOG_LEVEL_WARNING)
        ErrorDialog(parent).show_dialog(error_key, False)

    @staticmethod
    def _notification_handler(
        notification_texts: dict[str, str], key: str, default: str
    ) -> None:
        if notification_texts is None:
            return
        notification = NotificationDialog(
            AppContext.MAIN_WINDOW, notification_texts.get(key, default)
        )
        notification.show_notification()
