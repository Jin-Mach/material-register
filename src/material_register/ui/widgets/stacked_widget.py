from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStackedWidget

from src.material_register.ui.transactions.ui.transactions_widget import TransactionsWidget

if TYPE_CHECKING:
    from src.material_register.ui.main_window import MainWindow


class StackedWidget(QStackedWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.register_widget = TransactionsWidget(main_window)
        self.init_setup()

    def init_setup(self) -> None:
        widgets = [self.register_widget]
        for widget in widgets:
            self.addWidget(widget)