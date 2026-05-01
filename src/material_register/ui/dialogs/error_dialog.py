from PySide6.QtGui import QFont, QShowEvent, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QApplication

from material_register.ui.setup.texts_setup import TextsSetup


# noinspection PyTypeChecker
class ErrorDialog(QDialog):
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
        if not TextsSetup.set_ui_texts(self, [self.close_dialog_button, self.close_app_button]):
            self.close_dialog_button.setText("Close")
            self.close_dialog_button.setToolTip("Close the error dialog")
            self.close_dialog_button.setToolTipDuration(5000)
            self.close_app_button.setText("Exit")
            self.close_app_button.setToolTip("Exit the application")
            self.close_app_button.setToolTipDuration(5000)

    def _create_connection(self) -> None:
        self.close_dialog_button.clicked.connect(self.close)
        self.close_app_button.clicked.connect(ErrorDialog._close_app)

    def show_dialog(self, error_text: str, close_app: bool) -> None:
        self.error_text_label.setText(error_text)
        self.close_dialog_button.setVisible(not close_app)
        self.close_app_button.setVisible(close_app)
        self.exec()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        parent = QApplication.activeWindow()
        if parent:
            geometry = parent.frameGeometry()
        else:
            geometry = self.screen().availableGeometry()
        frame = self.frameGeometry()
        frame.moveCenter(geometry.center())
        self.move(frame.topLeft())

    @staticmethod
    def _close_app() -> None:
        QApplication.exit(1)