from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout

from material_register.controllers.transactions_controller import TransactionsController
from material_register.ui.transactions.transactions_widgets.transactions_view import TransactionsView
from material_register.ui.transactions.transactions_widgets.transactions_actions_widget import TransactionsActionsWidget

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class TransactionsWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.stacked_widget = stacked_widget
        self.transactions_controller = TransactionsController(self)
        self.setLayout(self.create_ui())
        self._create_connection()

    def create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.actions_widget = TransactionsActionsWidget(self.stacked_widget)
        self.transactions_view = TransactionsView(self.stacked_widget)
        main_layout.addWidget(self.actions_widget)
        main_layout.addWidget(self.transactions_view)
        return main_layout

    def _create_connection(self) -> None:
        self.actions_widget.in_transaction_button.clicked.connect(self.transactions_controller.create_transaction)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.setFocus()