from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer
from PySide6.QtWidgets import QWidget

from material_register.core.app_context import AppContext
from material_register.providers.paths_provider import PathsProvider
from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_WARNING, LOGGER_EXPORT
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.notification_dialog import NotificationDialog
from material_register.ui.dialogs.progress_dialog import ProgressDialog
from material_register.ui.setup.ui_texts import UiTexts
from material_register.workers.menu_workers.export_logs_data_worker import (
    ExportLogsDataWorker,
)

if TYPE_CHECKING:
    from material_register.ui.widgets.menu_bar import MenuBar


class ExportLogsDataController(QObject):
    def __init__(self, menu_bar: "MenuBar") -> None:
        super().__init__(menu_bar)
        self.menu_bar = menu_bar
        self.ui_texts = UiTexts.UI_TEXTS
        self._notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("EXPORT", None)
        self.progress_dialog = None
        self.worker = None
        self.thread = None

    def start_export(self) -> None:
        logs_path = PathsProvider.logs
        result = self.menu_bar.get_export_logs_path()
        if result is None:
            return
        export_path, displayed_path = result
        if export_path.exists():
            question = MessageBoxes.show_question(
                AppContext.MAIN_WINDOW,
                "FILE_EXISTS",
                displayed_path,
            )
            if not question:
                return
        self.progress_dialog = ProgressDialog(self.ui_texts, AppContext.MAIN_WINDOW)
        self.progress_dialog.set_label_text("exportInProgressText")
        self.progress_dialog.show()
        self._start_worker(logs_path, export_path)

    def _start_worker(self, logs_path: Path, export_path: Path) -> None:
        if self.thread is not None or self.worker is not None:
            return
        self.thread = QThread()
        self.worker = ExportLogsDataWorker(logs_path, export_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._export_ok)
        self.worker.error.connect(self._export_error)
        self.thread.start()

    def _export_error(self, error: str) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, lambda: self._finish_export(error=error))

    def _export_ok(self) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, self._finish_export)

    def _clean_thread(self) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _reset_variables(self) -> None:
        self.progress_dialog = None
        self.worker = None
        self.thread = None

    def _finish_export(self, error: str | None = None) -> None:
        self.progress_dialog.close()
        self._reset_variables()
        if error is not None:
            ExportLogsDataController._handle_export_error(
                error,
                f"{self.__class__.__name__}._export_error",
                AppContext.MAIN_WINDOW,
            )
            return
        ExportLogsDataController._notification_handler(
            self._notification_texts,
            "EXPORT_COMPLETED",
            "Export completed",
        )

    @staticmethod
    def _handle_export_error(
        error: str, method: str, parent: QWidget, error_key: str = "EXPORT_ERROR"
    ) -> None:
        if not error:
            error = f"Unknown export error: {method}"
        ErrorHandler.handle_error(
            f"{error}: {method}", LOGGER_EXPORT, LOG_LEVEL_WARNING
        )
        ErrorDialog(parent).show_dialog(error_key, False)

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
