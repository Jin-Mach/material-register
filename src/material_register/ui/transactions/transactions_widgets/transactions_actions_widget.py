from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class TransactionsActionsWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.setLayout(self.create_ui())

    def create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        self.add_transaction_button = QPushButton("Add Action")
        self.add_transaction_button.setObjectName("addTransactionButton")
        self.delete_transaction_button = QPushButton("Delete Action")
        self.delete_transaction_button.setObjectName("deleteTransactionButton")
        main_layout.addWidget(self.add_transaction_button)
        main_layout.addWidget(self.delete_transaction_button)
        main_layout.addStretch()
        return main_layout