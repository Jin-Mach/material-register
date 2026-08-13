from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QShowEvent
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout, QWidget


class ProgressDialog(QDialog):
    def __init__(
        self, export_texts: dict[str, dict[str, str]], parent: QWidget
    ) -> None:
        super().__init__(parent)
        self.setObjectName("progressDialog")
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.progress_texts = export_texts.get(self.__class__.__name__, {})
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        self.progress_label = QLabel()
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setRange(0, 0)
        main_layout.addWidget(self.progress_label)
        main_layout.addWidget(self.progress_bar)
        return main_layout

    def set_label_text(self, text_key: str) -> None:
        if self.progress_texts:
            self.progress_label.setText(self.progress_texts.get(text_key, "N/A"))

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Escape:
            event.ignore()
            return
        super().keyPressEvent(event)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.adjustSize()
        self.setFixedSize(self.width(), self.height())
