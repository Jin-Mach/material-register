from PySide6.QtGui import QFont, QShowEvent, Qt
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.error_texts import ErrorTexts
from material_register.ui.setup.ui_texts import UiTexts


# noinspection PyTypeChecker
class ErrorDialog(QDialog):
    DEFAULT_ERROR_TEXTS = {
        "APP_INIT_FAILED": "The application could not be started.",
        "RESOURCES_MISSING": "Required application files are missing.",
        "DOWNLOAD_FAILED": "Failed to download required files.",
        "TEXTS_LOAD_FAILED": "Failed to load application texts.",
        "ICONS_LOAD_FAILED": "Failed to load application icons",
        "CONFIG_LOAD_FAILED": "Failed to load application settings.",
        "SETTINGS_FAILED": "An error occurred while configuring the application.",
        "DATABASE_FAILED": "Failed to connect to or load the database.",
        "DATABASE_ERROR": "An error occurred while working with the database.",
        "EXPORT_ERROR": "Failed to complete the export.",
        "PATH_ERROR": "Error while setting the file path.",
        "CRITICAL_FAILURE": "A critical error occurred.",
        "UNKNOWN_ERROR": "An unexpected error occurred.",
        "CONNECTION_ERROR": "Unable to establish an internet connection.",
        "PERMISSION_ERROR": "The application does not have permission to write to disk.",
    }

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.setLayout(self._create_ui())
        self._setup_texts()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.error_text_label = QLabel()
        self.error_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.error_text_label.setFont(font)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel
            | QDialogButtonBox.StandardButton.Close
        )
        self.close_dialog_button = button_box.button(
            QDialogButtonBox.StandardButton.Cancel
        )
        self.close_dialog_button.setObjectName("closeDialogButton")
        self.close_app_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.close_app_button.setObjectName("closeAppButton")
        main_layout.addWidget(self.error_text_label)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_texts(self) -> None:
        widgets = [self.close_dialog_button, self.close_app_button]
        if UiTexts.set_ui_texts(self, widgets):
            return
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.close_dialog_button.clicked.connect(self.close)
        self.close_app_button.clicked.connect(ErrorDialog._close_app)

    def show_dialog(self, error_key: str, close_app: bool) -> None:
        text = ErrorTexts.ERROR_TEXTS.get(
            error_key, self.DEFAULT_ERROR_TEXTS.get(error_key, "UNKNOWN_ERROR")
        )
        self.error_text_label.setText(text)
        self.close_dialog_button.setVisible(not close_app)
        self.close_app_button.setVisible(close_app)
        self.exec()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        centre_dialog(self)

    @staticmethod
    def _close_app() -> None:
        QApplication.exit(1)
