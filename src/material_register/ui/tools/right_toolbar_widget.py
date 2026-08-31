from typing import TYPE_CHECKING

from PySide6.QtGui import Qt
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class RightToolbarWidget(QWidget):
    WIDTH = 40
    BUTTON_SIZE = 30

    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.setFixedWidth(self.WIDTH)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.test_button = QPushButton()
        self.test_button.setFixedSize(QSize(self.BUTTON_SIZE, self.BUTTON_SIZE))
        main_layout.addWidget(self.test_button)
        main_layout.addStretch()
        return main_layout