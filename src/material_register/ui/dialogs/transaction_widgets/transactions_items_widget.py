from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableView, QSizePolicy

if TYPE_CHECKING:
    from material_register.ui.dialogs.transaction_items_dialog import TransactionItemsDialog


class TransactionsItemsWidget(QWidget):
    def __init__(self, transaction_item_dialog: "TransactionItemsDialog"):
        super().__init__(transaction_item_dialog)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.transactions_items_view = QTableView()
        self.transactions_items_view.setObjectName("transactionsItemsView")
        buttons_price_layout = QHBoxLayout()
        self.add_item_button = QPushButton("Add")
        self.add_item_button.setObjectName("addItemButton")
        self.delete_item_button = QPushButton("Delete")
        self.delete_item_button.setObjectName("deleteButton")
        self.total_price_label = QLabel("Total:")
        self.total_price_label.setObjectName("totalPriceLabel")
        self.total_price = QLabel("1000")
        buttons_price_layout.addWidget(self.add_item_button)
        buttons_price_layout.addWidget(self.delete_item_button)
        buttons_price_layout.addStretch()
        buttons_price_layout.addWidget(self.total_price_label)
        buttons_price_layout.addWidget(self.total_price)
        main_layout.addWidget(self.transactions_items_view)
        main_layout.addLayout(buttons_price_layout)
        return main_layout