from typing import TYPE_CHECKING

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QMessageBox

from material_register.db.models.transaction_items_model import TransactionItemsModel
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.transaction_widgets.transaction_view import TransactionView
from material_register.ui.helpers.styles import PRICE_STYLE
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
        self.transactions_items_view = TransactionView(self)
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
        self.total_price = QLabel()
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
        self._setup_style()
        self._setup_model()
        self.transactions_items_view.setup_ui()

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        ui_texts = UiTexts.UI_TEXTS
        self.price_suffix = ui_texts.get(self.__class__.__name__, {}).get("priceSuffix", "")
        self.total_price.setText(f"{0} {self.price_suffix}")
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_style(self) -> None:
        font = QFont()
        font.setBold(True)
        self.total_price.setStyleSheet(PRICE_STYLE)
        self.total_price.setFont(font)

    def _setup_model(self) -> None:
        self.transaction_item_model = TransactionItemsModel(self.price_suffix)
        self.transactions_items_view.setModel(self.transaction_item_model)

    def add_item(self, new_item_data:  dict[str, str | int | float] | None) -> None:
        if new_item_data is None:
            MessageBoxes.show_error(self, "ITEMS_DATA_FAILED", QMessageBox.Icon.Warning)
            return
        self.transaction_item_model.add_item(new_item_data)
        self.total_price.setText(self.transaction_item_model.return_total_price())