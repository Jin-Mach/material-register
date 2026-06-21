from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSizePolicy

from material_register.config.app_constants import TRANSFER_OUT, TRANSFER_IN
from material_register.db.models.transaction_items_model_in import TransactionItemsModelIn
from material_register.db.models.transaction_items_model_out import TransactionItemsModelOut
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.transaction_widgets.transaction_view import TransactionView
from material_register.ui.helpers.styles import PRICE_STYLE
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.transaction_items_dialog_in import TransactionItemsDialogIn
    from material_register.ui.dialogs.transaction_items_dialog_out import TransactionItemsDialogOut


class TransactionsItemsWidget(QWidget):
    def __init__(self, transaction_items_dialog: "TransactionItemsDialogIn | TransactionItemsDialogOut", transfer_type: str):
        super().__init__(transaction_items_dialog)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.transaction_items_dialog = transaction_items_dialog
        self.transfer_type = transfer_type
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
        self.total_value_label = QLabel()
        buttons_price_layout.addWidget(self.add_item_button)
        buttons_price_layout.addWidget(self.update_item_button)
        buttons_price_layout.addWidget(self.delete_item_button)
        buttons_price_layout.addStretch()
        buttons_price_layout.addWidget(self.total_price_label)
        buttons_price_layout.addWidget(self.total_value_label)
        main_layout.addWidget(self.transactions_items_view)
        main_layout.addLayout(buttons_price_layout)
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [self.add_item_button, self.update_item_button, self.delete_item_button, self.total_price_label]
        disabled_buttons = [self.update_item_button, self.delete_item_button]
        for button in disabled_buttons:
            button.setEnabled(False)
        self._setup_texts(widgets)
        self._setup_style()
        self._setup_model(self.transfer_type)
        self.transactions_items_view.setup_ui()
        self._create_connection()

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        ui_texts = UiTexts.UI_TEXTS
        self.price_suffix = ui_texts.get(self.__class__.__name__, {}).get("priceSuffix", "")
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_style(self) -> None:
        font = QFont()
        font.setBold(True)
        self.total_value_label.setStyleSheet(PRICE_STYLE)
        self.total_value_label.setFont(font)

    def _setup_model(self, transfer_type: str) -> None:
        if transfer_type == TRANSFER_IN:
            self.transaction_item_model_in = TransactionItemsModelIn(self.price_suffix)
            self.transactions_items_view.setModel(self.transaction_item_model_in)
            self.current_model = self.transaction_item_model_in
        elif transfer_type == TRANSFER_OUT:
            self.transaction_item_model_out = TransactionItemsModelOut()
            self.transactions_items_view.setModel(self.transaction_item_model_out)
            self.current_model = self.transaction_item_model_out

    def _create_connection(self) -> None:
        selection_model = self.transactions_items_view.selectionModel()
        if selection_model:
            selection_model.selectionChanged.connect(self._update_buttons_state)
        self.current_model.rowsInserted.connect(self._update_save_button_state)
        self.current_model.rowsRemoved.connect(self._update_save_button_state)
        self.current_model.modelReset.connect(self._update_save_button_state)

    def _check_selection(self) -> bool:
        return self.transactions_items_view.selectionModel().hasSelection()

    def _update_buttons_state(self) -> None:
        state = self._check_selection()
        self.update_item_button.setEnabled(state)
        self.delete_item_button.setEnabled(state)

    def _update_save_button_state(self) -> None:
        state = self.current_model.rowCount() > 0
        self.transaction_items_dialog.save_transaction_button.setEnabled(state)

    def get_selected_index(self) -> QModelIndex | None:
        index = self.transactions_items_view.selectionModel().currentIndex()
        if not index.isValid():
            return None
        return index

    def add_item(self, new_item_data: dict[str, str | int | float] | None) -> None:
        if new_item_data is None:
            MessageBoxes.show_error(self, "ITEMS_DATA_FAILED", "WARNING")
            return
        self.current_model.add_item(new_item_data)
        self._setup_total_value(self.current_model)

    def update_item(self, index: QModelIndex, item_data: dict[str, str | int | float]) -> None:
        if item_data is None:
            MessageBoxes.show_error(self, "ITEMS_DATA_FAILED", "WARNING")
            return
        row = index.row()
        self.current_model.update_item(row, item_data)
        self._setup_total_value(self.current_model)

    def delete_item(self, index: QModelIndex) -> None:
        self.current_model.delete_item(index)
        self._setup_total_value(self.current_model)

    def _setup_total_value(self, current_model: TransactionItemsModelIn | TransactionItemsModelOut) -> None:
        self.total_value_label.setText(current_model.return_total())