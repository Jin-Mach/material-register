from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

if TYPE_CHECKING:
    from src.material_register.ui.main_window import MainWindow


class SidePanel(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setLayout(self.create_ui())

    def create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.register_button = QPushButton("Register")
        self.register_button.setObjectName("registerButton")
        main_layout.addWidget(self.register_button)
        main_layout.addStretch()
        return main_layout