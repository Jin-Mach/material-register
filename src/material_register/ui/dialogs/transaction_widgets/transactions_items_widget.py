from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableView, QSizePolicy

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.transaction_items_dialog import TransactionItemsDialog


class TransactionsItemsWidget(QWidget):
    def __init__(self, transaction_item_dialog: "TransactionItemsDialog"):
        super().__init__(transaction_item_dialog)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.transactions_items_view = QTableView()
        self.transactions_items_view.setObjectName("transactionsItemsView")
        buttons_price_layout = QHBoxLayout()
        self.add_item_button = QPushButton()
        self.add_item_button.setObjectName("addItemButton")
        self.update_item_button = QPushButton()
        self.update_item_button.setObjectName("updateItemButton")
        self.delete_item_button = QPushButton()
        self.delete_item_button.setObjectName("deleteButton")
        self.total_price_label = QLabel()
        self.total_price_label.setObjectName("totalPriceLabel")
        self.total_price = QLabel("1000")
        buttons_price_layout.addWidget(self.add_item_button)
        buttons_price_layout.addWidget(self.update_item_button)
        buttons_price_layout.addWidget(self.delete_item_button)
        buttons_price_layout.addStretch()
        buttons_price_layout.addWidget(self.total_price_label)
        buttons_price_layout.addWidget(self.total_price)
        main_layout.addWidget(self.transactions_items_view)
        main_layout.addLayout(buttons_price_layout)
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [self.add_item_button, self.update_item_button, self.delete_item_button, self.total_price_label]
        self._setup_texts(widgets)

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)