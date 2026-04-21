from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.material_register.ui.register.ui.register_widgets.table_view_widget import TableViewWidget
from src.material_register.ui.register.ui.register_widgets.actions_widget import ActionsWidget

if TYPE_CHECKING:
    from src.material_register.ui.main_window import MainWindow


class RegisterWidget(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setLayout(self.create_ui())

    def create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.actions_widget = ActionsWidget(self.main_window)
        self.table_view = TableViewWidget(self.main_window)
        main_layout.addWidget(self.actions_widget)
        main_layout.addWidget(self.table_view)
        return main_layout