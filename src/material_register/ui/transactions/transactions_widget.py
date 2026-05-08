from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout

from material_register.ui.transactions.transactions_widgets.transactions_view import TransactionsView
from material_register.ui.transactions.transactions_widgets.transactions_actions_widget import TransactionsActionsWidget

if TYPE_CHECKING:
    from src.material_register.ui.main_window import MainWindow


class TransactionsWidget(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setLayout(self.create_ui())

    def create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.actions_widget = TransactionsActionsWidget(self.main_window)
        self.table_view = TransactionsView(self.main_window)
        main_layout.addWidget(self.actions_widget)
        main_layout.addWidget(self.table_view)
        return main_layout