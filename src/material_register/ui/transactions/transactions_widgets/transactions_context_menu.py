from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu


if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widgets.transactions_view import TransactionsView
    from material_register.controllers.transactions_controller import TransactionsController


class TransactionsContextMenu(QMenu):
    def __init__(self, transactions_view: "TransactionsView", transactions_controller: "TransactionsController") -> None:
        super().__init__(transactions_view)
        self.transactions_controller = transactions_controller
        self._create_ui()
        self._create_connection()
        self.transaction_index = None

    def _create_ui(self) -> None:
        self.update_transaction_action = QAction(self)
        self.update_transaction_action.setObjectName("updateTransactionAction")
        self.delete_transaction_action = QAction(self)
        self.delete_transaction_action.setObjectName("deleteTransactionAction")
        self.addAction(self.update_transaction_action)
        self.addAction(self.delete_transaction_action)

    def set_ui_texts(self, ui_texts: dict[str, str]) -> None:
        if ui_texts:
            for widget in self.findChildren(QAction):
                key = widget.objectName() + "Text"
                if key in ui_texts:
                    widget.setText(ui_texts[key])

    def _create_connection(self) -> None:
        self.update_transaction_action.triggered.connect(self._update_transaction)
        self.delete_transaction_action.triggered.connect(self._delete_transaction)

    def set_customer_index(self, index: QModelIndex) -> None:
        self.transaction_index= index

    def _update_transaction(self) -> None:
        if self.transaction_index is None:
            return
        self.transactions_controller.update_transaction(self.transaction_index)

    def _delete_transaction(self) -> None:
        if self.transaction_index is None:
            return
        self.transactions_controller.delete_transaction(self.transaction_index)