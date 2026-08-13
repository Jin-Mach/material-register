from typing import TYPE_CHECKING

from PySide6.QtCore import QPropertyAnimation, Qt, QTimer
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from material_register.ui.helpers.window_positioning import get_notification_position

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class NotificationDialog(QDialog):
    def __init__(self, main_window: "MainWindow", notification_text: str) -> None:
        super().__init__(main_window)
        self.setObjectName("notificationDialog")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool)
        self.main_window = main_window
        self.notification_text = notification_text
        self.setLayout(self._create_ui())
        self._setup_texts()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.notification_label = QLabel()
        main_layout.addWidget(self.notification_label)
        return main_layout

    def _setup_texts(self) -> None:
        self.notification_label.setText(self.notification_text)

    def _fade_in(self, duration: int = 1000) -> None:
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()
        QTimer.singleShot(3000, self._fade_out_and_close)

    def _fade_out_and_close(self, duration: int = 1000) -> None:
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(duration)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.finished.connect(self.close)
        self.animation.start()

    def show_notification(self) -> None:
        self.adjustSize()
        self.setFixedSize(self.size())
        position = get_notification_position(self)
        self.move(position)
        self.setWindowOpacity(0.0)
        self.show()
        self._fade_in()
