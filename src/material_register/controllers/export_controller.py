from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, QObject
from PySide6.QtSql import QSqlDatabase

from material_register.core.app_context import AppContext
from material_register.providers.settings_provider import SettingsProvider
from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.notification_dialog import NotificationDialog
from material_register.workers.export_worker import ExportWorker

if TYPE_CHECKING:
    from material_register.ui.export.export_widget import ExportWidget


class ExportController(QObject):
    def __init__(self, export_widget: "ExportWidget") -> None:
        super().__init__()
        self.export_widget = export_widget
        self.export_settings = {}
        self.thread = None
        self.worker = None
        self.notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("EXPORT", None)
        self.status_texts = TextsProvider.STATUS_TEXTS

    def start_export(self) -> None:
        self.export_settings = self.export_widget.get_export_data()
        if not self._is_export_settings_valid():
            return
        self._start_worker(self.export_settings["pathLineEdit"], self.export_settings["from_date"],
                           self.export_settings["to_date"])

    def _start_worker(self, export_path: Path, from_date: str, to_date: str) -> None:
        self.thread = QThread()
        self.worker = ExportWorker(export_path, from_date, to_date)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._export_error)
        self.worker.finished.connect(self._export_ok)
        self.thread.start()

    def _export_error(self, error: str) -> None:
        self._clean_thread()
        ExportController._handle_export_error(error, f"{self.__class__.__name__}._export_error")

    def _export_ok(self) -> None:
        self._clean_thread()
        if self.export_settings.get("useLastOptionsCheckbox", False):
            self._last_settings_saved()
        ExportController._notification_handler(self.notification_texts, "EXPORT_COMPLETED", "Export completed")

    def _clean_thread(self) -> None:
        if self.worker and self.worker.db_connection:
            connection_name = self.worker.db_connection.connectionName()
            self.worker.db_connection.close()
            self.worker.db_connection = None
            QSqlDatabase.removeDatabase(connection_name)
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.export_settings = {}
        self.thread = None
        self.worker = None

    def _last_settings_saved(self) -> None:
        user_settings = SettingsProvider.SETTINGS.get("user", {})
        if not user_settings:
            AppContext.MAIN_WINDOW.status_bar.show_message(self.status_texts.get("SETTINGS_FAILED"))
            return
        for key, value in self.export_settings.items():
            if key in user_settings:
                user_settings[key] = value
        if not SettingsProvider.save_settings():
            AppContext.MAIN_WINDOW.status_bar.show_message(self.status_texts.get("SETTINGS_FAILED"))
            return
        self._reload_settings()
        AppContext.MAIN_WINDOW.status_bar.show_message(self.status_texts.get("SETTINGS_SAVED"))

    def _reload_settings(self) -> None:
        stacked_widget = self.export_widget.stacked_widget
        export_settings = stacked_widget.settings_widget.export_settings
        if hasattr(self.export_widget, "apply_settings"):
            self.export_widget.apply_settings()
        if hasattr(export_settings, "apply_settings"):
            export_settings.apply_settings()

    def _is_export_settings_valid(self) -> bool:
        required_keys = [
            "branchNameLineEdit",
            "pathLineEdit",
            "fileNameLineEdit",
            "from_date",
            "to_date",
            "opening_balance",
            "income",
            "expense",
            "noActionRadioButton",
            "openFolderRadioButton",
            "openFileRadioButton",
            "useLastOptionsCheckbox",
            "saveLastOpeningBalanceCheckbox"
        ]
        for key in required_keys:
            if key not in self.export_settings:
                return False
        for key in ["branchNameLineEdit", "pathLineEdit", "fileNameLineEdit", "from_date", "to_date"]:
            if self.export_settings[key] in (None, ""):
                return False
        for key in ["opening_balance", "income", "expense"]:
            if not isinstance(self.export_settings[key], (int, float)):
                return False
        for key in ["noActionRadioButton", "openFolderRadioButton", "openFileRadioButton", "useLastOptionsCheckbox",
                    "saveLastOpeningBalanceCheckbox"]:
            if not isinstance(self.export_settings[key], bool):
                return False
        return True

    @staticmethod
    def _handle_export_error(error: str, method: str) -> None:
        if not error:
            error = f"Unknown export error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", "export", "critical")
        dialog = ErrorDialog()
        dialog.show_dialog("EXPORT_ERROR", False)

    @staticmethod
    def _notification_handler(notification_texts: dict[str, str], key: str, default: str) -> None:
        if notification_texts is None:
            return
        notification = NotificationDialog(AppContext.MAIN_WINDOW, notification_texts.get(key, default))
        notification.show_notification()