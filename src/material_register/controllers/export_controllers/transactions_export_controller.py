from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer
from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import QWidget

from material_register.config.ui_constants import (
    EXPORT_TYPE_TRANSACTIONS,
    TRANSFER_IN,
    TRANSFER_OUT,
)
from material_register.core.app_context import AppContext
from material_register.providers.settings_provider import SettingsProvider
from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.notification_dialog import NotificationDialog
from material_register.ui.dialogs.progress_dialog import ProgressDialog
from material_register.utils.file_launchers import (
    open_file_in_default,
    open_file_in_explorer,
)
from material_register.workers.export_workers.transactions_export_worker import (
    TransactionsExportWorker,
)

if TYPE_CHECKING:
    from material_register.ui.export.export_widgets.transactions_export_widget import (
        TransactionsExportWidget,
    )


class TransactionsExportController(QObject):
    def __init__(self, transactions_export_widget: "TransactionsExportWidget") -> None:
        super().__init__()
        self.transactions_export_widget = transactions_export_widget
        self.export_path = None
        self.progress_dialog = None
        self.export_settings = {}
        self.thread = None
        self.worker = None
        self.notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("EXPORT", None)
        self.export_texts = TextsProvider.EXPORT_TEXTS

    def start_export(self) -> None:
        self.export_settings = self.transactions_export_widget.get_export_data()
        if not self._is_export_settings_valid():
            MessageBoxes.show_error(self.transactions_export_widget, "INVALID_DATA")
            return
        if not self.export_texts:
            TransactionsExportController._handle_export_error(
                "Export texts not loaded",
                f"{self.__class__.__name__}.start_export",
                self.transactions_export_widget,
                "TEXTS_LOAD_FAILED",
            )
            return
        self.export_path = self.export_settings.get("export_path", None)
        if self.export_path is None:
            TransactionsExportController._handle_export_error(
                "Export path is None",
                f"{self.__class__.__name__}.start_export",
                self.transactions_export_widget,
                "PATH_ERROR",
            )
            return
        if self._has_existing_export_files():
            question = MessageBoxes.show_question(
                self.transactions_export_widget, "FILE_EXISTS"
            )
            if not question:
                return
        self.export_path.mkdir(parents=True, exist_ok=True)
        self.progress_dialog = ProgressDialog(self.export_texts, AppContext.MAIN_WINDOW)
        self.progress_dialog.set_label_text("loadingDataText")
        self.progress_dialog.show()
        self._start_worker(self.export_settings, self.export_texts)

    def _start_worker(
        self,
        export_settings: dict[str, Path | str | int | None | bool],
        export_texts: dict[str, dict[str, str]],
    ) -> None:
        self.thread = QThread()
        self.worker = TransactionsExportWorker(export_settings, export_texts)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._export_error)
        self.worker.no_export_data.connect(self._no_export_data)
        self.worker.export_started.connect(self._update_texts)
        self.worker.finished.connect(self._export_ok)
        self.thread.start()

    def _no_export_data(self, key: str) -> None:
        self._clean_thread()
        self.progress_dialog.close()
        self._reset_variables()
        QTimer.singleShot(
            100,
            lambda: MessageBoxes.show_error(self.transactions_export_widget, key),
        )

    def _update_texts(self) -> None:
        self.progress_dialog.set_label_text("exportInProgressText")

    def _export_error(self, error: str) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, lambda: self._finish_export(error=error))

    def _export_ok(self) -> None:
        if self.export_settings.get("useLastOptionsCheckbox", False):
            self._last_settings_saved()
        self._clean_thread()
        QTimer.singleShot(1000, self._finish_export)

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

    def _reset_variables(self) -> None:
        self.export_settings = {}
        self.progress_dialog = None
        self.export_path = None
        self.thread = None
        self.worker = None

    def _finish_export(self, error: str | None = None) -> None:
        self.progress_dialog.close()
        if error is not None:
            TransactionsExportController._handle_export_error(
                error,
                f"{self.__class__.__name__}._export_error",
                self.transactions_export_widget,
            )
            self._reset_variables()
            return
        TransactionsExportController._notification_handler(
            self.notification_texts,
            "EXPORT_COMPLETED",
            "Export completed",
        )
        if self.export_settings.get(
            "openFolderRadioButton", False
        ) and not open_file_in_explorer(self.export_path):
            MessageBoxes.show_error(
                self.transactions_export_widget,
                "OPEN_EXPLORER_FAILED",
                "INFORMATION",
            )
        if self.export_settings.get(
            "openFileRadioButton", False
        ) and not open_file_in_default(self.export_path):
            MessageBoxes.show_error(
                self.transactions_export_widget,
                "OPEN_FILE_FAILED",
                "INFORMATION",
            )

        self._reset_variables()

    def _has_existing_export_files(self) -> bool:
        export_path = self.export_settings.get("export_path")
        if export_path is None:
            return False
        if not export_path.exists():
            return False
        transfer_in, transfer_out = self.export_settings.get(
            "transfer_type", (TRANSFER_IN, None)
        )
        prefixes = []
        if transfer_in is not None:
            prefixes.append(
                self.export_texts["TransactionsSheet"].get(TRANSFER_IN, TRANSFER_IN)
            )
        if transfer_out is not None:
            prefixes.append(
                self.export_texts["TransactionsSheet"].get(TRANSFER_OUT, TRANSFER_OUT)
            )
        for item in export_path.iterdir():
            if item.is_file() and item.name.startswith(tuple(prefixes)):
                return True
        return False

    def _last_settings_saved(self) -> None:
        user_settings_keys = [
            "branchNameLineEdit",
            "pathLineEdit",
            "fileNameLineEdit",
            "noActionRadioButton",
            "openFolderRadioButton",
            "openFileRadioButton",
            "useLastOptionsCheckbox",
        ]
        user_settings = (
            SettingsProvider.SETTINGS.get("export", {})
            .get(EXPORT_TYPE_TRANSACTIONS, {})
            .get("user", {})
        )
        if not user_settings:
            AppContext.MAIN_WINDOW.status_bar.show_message("SETTINGS_FAILED")
            return
        for key, value in self.export_settings.items():
            if isinstance(value, Path):
                value = str(value)
            if key in user_settings_keys:
                user_settings[key] = value
        if not SettingsProvider.save_settings():
            AppContext.MAIN_WINDOW.status_bar.show_message("SETTINGS_FAILED")
            return
        AppContext.MAIN_WINDOW.status_bar.show_message("SETTINGS_SAVED")

    def _is_export_settings_valid(self) -> bool:
        required_keys = [
            "branchNameLineEdit",
            "pathLineEdit",
            "fileNameLineEdit",
            "from_date",
            "to_date",
            "split_by_month",
            "customer_id",
            "transfer_type",
            "noActionRadioButton",
            "openFolderRadioButton",
            "openFileRadioButton",
            "useLastOptionsCheckbox",
        ]
        for key in required_keys:
            if key not in self.export_settings:
                return False
        for key in [
            "branchNameLineEdit",
            "pathLineEdit",
            "fileNameLineEdit",
            "from_date",
            "to_date",
        ]:
            if self.export_settings[key] in (None, ""):
                return False
        if not isinstance(self.export_settings["split_by_month"], bool):
            return False
        if self.export_settings["customer_id"] is not None and not isinstance(
            self.export_settings["customer_id"], int
        ):
            return False
        if (
            not isinstance(self.export_settings["transfer_type"], tuple)
            or len(self.export_settings["transfer_type"]) != 2
        ):
            return False
        for key in [
            "noActionRadioButton",
            "openFolderRadioButton",
            "openFileRadioButton",
            "useLastOptionsCheckbox",
        ]:
            if not isinstance(self.export_settings[key], bool):
                return False
        return True

    @staticmethod
    def _handle_export_error(
        error: str,
        method: str,
        parent: QWidget,
        error_key: str = "EXPORT_ERROR",
    ) -> None:
        if not error:
            error = f"Unknown export error: {method}"
        ErrorHandler.handle_error(
            f"{error}: {method}",
            "export",
            "critical",
        )
        ErrorDialog(parent).show_dialog(error_key, False)

    @staticmethod
    def _notification_handler(
        notification_texts: dict[str, str],
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
