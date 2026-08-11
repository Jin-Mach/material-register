from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QShowEvent
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QStyle,
    QVBoxLayout,
)


# noinspection PyTypeChecker
class MessageBoxDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        icon_texts_layout = QHBoxLayout()
        self.icon_label = QLabel()
        texts_layout = QVBoxLayout()
        self.text_label = QLabel()
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.informative_label = QLabel()
        self.informative_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        texts_layout.addWidget(self.text_label)
        texts_layout.addWidget(self.informative_label)
        icon_texts_layout.addWidget(self.icon_label)
        icon_texts_layout.addLayout(texts_layout)
        main_layout.addLayout(icon_texts_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        hide_widgets = [self.ok_button, self.cancel_button, self.informative_label]
        for widget in hide_widgets:
            widget.hide()
        self._setup_style()

    def _setup_style(self) -> None:
        font = QFont()
        font.setBold(True)
        self.text_label.setFont(font)

    def _create_connection(self) -> None:
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def setup_texts(self, title: str, text: str, ok_button: str="", cancel_button: str="", informative_text: str="") -> None:
        self.setWindowTitle(title)
        self.text_label.setText(text)
        if ok_button:
            self.ok_button.setText(ok_button)
            self.ok_button.show()
        if cancel_button:
            self.cancel_button.setText(cancel_button)
            self.cancel_button.show()
        if informative_text:
            self.informative_label.setText(informative_text)
            self.informative_label.show()

    def setup_icon(self, icon_key: str=None) -> None:
        app_style = QApplication.style()
        icon_map = {
            "QUESTION": app_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion),
            "INFORMATION": app_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation),
            "WARNING": app_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning),
            "CRITICAL": app_style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
        }
        if icon_key is None:
            icon_key = "WARNING"
        icon = icon_map.get(icon_key, None)
        if icon is None:
            return
        self.icon_label.setPixmap(icon.pixmap(32, 32))

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.adjustSize()
        self.setFixedSize(self.size())