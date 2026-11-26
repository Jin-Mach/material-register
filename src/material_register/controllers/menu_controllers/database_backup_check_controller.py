from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QStandardPaths, QThread, QTimer
from PySide6.QtWidgets import QFileDialog, QWidget

from material_register.core.app_context import AppContext
from material_register.providers.paths_provider import PathsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_WARNING, LOGGER_DB
from material_register.ui.dialogs.error_dialog import ErrorDialog
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
        self.worker.error.connect(self._check_error)
        self.thread.start()

    def _check_error(self, error: str) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, lambda: self._finish_check(error=error))

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

    def _finish_check(self, error: str | None = None) -> None:
        self.progress_dialog.close()
        self._reset_variables()
        if error is not None:
            DatabaseBackupCheckController._handle_export_error(
                error,
                f"{self.__class__.__name__}._database_backup_check_error",
                AppContext.MAIN_WINDOW,
            )
            self.custom_check = None
            return
        self.custom_check = None
        print("OK")

    @staticmethod
    def _handle_export_error(
        error: str, method: str, parent: QWidget, error_key: str = "DATABASE_ERROR"
    ) -> None:
        if not error:
            error = f"Unknown export error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", LOGGER_DB, LOG_LEVEL_WARNING)
        ErrorDialog(parent).show_dialog(error_key, False)
