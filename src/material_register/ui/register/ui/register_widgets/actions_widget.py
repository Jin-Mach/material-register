from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

if TYPE_CHECKING:
    from src.material_register.ui.main_window import MainWindow


class ActionsWidget(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.setLayout(self.create_ui())

    def create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        self.add_action = QPushButton("Add Action")
        self.add_action.setObjectName("addAction")
        self.delete_action = QPushButton("Delete Action")
        self.delete_action.setObjectName("deleteAction")
        main_layout.addWidget(self.add_action)
        main_layout.addWidget(self.delete_action)
        main_layout.addStretch()
        return main_layout