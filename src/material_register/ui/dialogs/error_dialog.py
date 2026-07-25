from PySide6.QtGui import QFont, QShowEvent, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QApplication

from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.error_texts import ErrorTexts
from material_register.ui.setup.ui_texts import UiTexts


# noinspection PyTypeChecker
class ErrorDialog(QDialog):
    DEFAULT_ERROR_TEXTS = {
        "APP_INIT_FAILED": "Application failed to start.",
        "RESOURCES_MISSING": "Required application resources are missing.",
        "CONNECTION_ERROR": "No internet connection available.",
        "PERMISSION_ERROR": "Application has no permission to write to disk.",
        "DOWNLOAD_FAILED": "Failed to download required application files.",
        "TEXTS_LOAD_FAILED": "Failed to load application text resources.",
        "UNKNOWN_ERROR": "An unexpected error occurred."
    }

    def __init__(self) -> None:
        super().__init__()
        self.setLayout(self._create_ui())
        self._ui_setup()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.error_text_label = QLabel()
        self.error_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.error_text_label.setFont(font)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Close)
        self.close_dialog_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.close_dialog_button.setObjectName("closeDialogButton")
        self.close_app_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.close_app_button.setObjectName("closeAppButton")
        main_layout.addWidget(self.error_text_label)
        main_layout.addWidget(button_box)
        return main_layout

    def _ui_setup(self) -> None:
        widgets = [self.close_dialog_button, self.close_app_button]
        if UiTexts.set_ui_texts(self, widgets):
            return
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.close_dialog_button.clicked.connect(self.close)
        self.close_app_button.clicked.connect(ErrorDialog._close_app)

    def show_dialog(self, error_key: str, close_app: bool) -> None:
        text = ErrorTexts.ERROR_TEXTS.get(error_key, self.DEFAULT_ERROR_TEXTS.get(error_key, "UNKNOWN_ERROR"))
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