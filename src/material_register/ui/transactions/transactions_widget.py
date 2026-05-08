from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout

from material_register.ui.transactions.transactions_widgets.transactions_view import TransactionsView
from material_register.ui.transactions.transactions_widgets.transactions_actions_widget import TransactionsActionsWidget

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class TransactionsWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.stacked_widget = stacked_widget
        self.setLayout(self.create_ui())

    def create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.actions_widget = TransactionsActionsWidget(self.stacked_widget)
        self.transactions_view = TransactionsView(self.stacked_widget)
        main_layout.addWidget(self.actions_widget)
        main_layout.addWidget(self.transactions_view)
        return main_layout

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.setFocus()