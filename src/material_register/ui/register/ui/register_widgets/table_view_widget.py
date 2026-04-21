from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTableView

if TYPE_CHECKING:
    from src.material_register.ui.main_window import MainWindow


class TableViewWidget(QTableView):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)