from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton

from material_register.ui.dialogs.transaction_widgets.transaction_info_widget import TransactionInfoWidget
from material_register.ui.dialogs.transaction_widgets.transactions_items_widget import TransactionsItemsWidget
from material_register.ui.helpers.window_positioning import centre_dialog

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


class TransactionItemsDialog(QDialog):
    def __init__(self, create_data: dict[str, str], transactions_widget: "TransactionsWidget") -> None:
        super().__init__(transactions_widget)
        self.setMinimumSize(800, 500)
        self.create_data = create_data
        self.transactions_widget = transactions_widget
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.transaction_info_widget = TransactionInfoWidget(self)
        self.transactions_items_widget = TransactionsItemsWidget(self)
        buttons_layout = QHBoxLayout()
        self.save_transactions_button = QPushButton("Save")
        self.save_transactions_button.setObjectName("saveTransactionsButton")
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setObjectName("cancelButton")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_transactions_button)
        buttons_layout.addWidget(self.cancel_button)
        main_layout.addWidget(self.transaction_info_widget)
        main_layout.addWidget(self.transactions_items_widget)
        main_layout.addLayout(buttons_layout)
        return main_layout

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        centre_dialog(self)