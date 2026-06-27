from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QDialog, QVBoxLayout, QWidget, QDialogButtonBox

from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.transaction_widgets.transaction_info_widget import TransactionInfoWidget
from material_register.ui.dialogs.transaction_widgets.transactions_items_widget import TransactionsItemsWidget
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.controllers.transactions_controller import TransactionsController
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


# noinspection PyTypeChecker
class TransactionItemsDialogOut(QDialog):
    def __init__(self, transactions_controller: "TransactionsController", create_data: dict[str, str | int],
                 transactions_widget: "TransactionsWidget", transfer_type: str) -> None:
        super().__init__(transactions_widget)
        self.setMinimumSize(800, 500)
        self.transactions_controller = transactions_controller
        self.create_data = create_data
        self.transactions_widget = transactions_widget
        self.transfer_type = transfer_type
        self.setLayout(self._create_ui())
        self._setup_ui()
        self.set_create_data(create_data)
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.transaction_info_widget = TransactionInfoWidget(self, self.transfer_type)
        self.transactions_items_widget = TransactionsItemsWidget(self, self.transfer_type)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.save_transaction_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.save_transaction_button.setObjectName("saveTransactionButton")
        self.cancel_transaction_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_transaction_button.setObjectName("cancelTransactionButton")
        main_layout.addWidget(self.transaction_info_widget)
        main_layout.addWidget(self.transactions_items_widget, 3)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [self.save_transaction_button, self.cancel_transaction_button]
        self.save_transaction_button.setEnabled(False)
        self._setup_texts(widgets)

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.cash_payment = ui_texts.get("CASH", "CASH")
        self.transfer_payment = ui_texts.get("TRANSFER", "TRANSFER")
        if not ui_texts:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _create_connection(self) -> None:
        self.save_transaction_button.clicked.connect(self.accept)
        self.cancel_transaction_button.clicked.connect(self.reject)
        self.transaction_info_widget.update_transaction_info_button.clicked.connect(self._update_create_data)
        self.transactions_items_widget.add_item_button.clicked.connect(self._add_transaction_item)
        self.transactions_items_widget.update_item_button.clicked.connect(self._update_transaction_item)
        self.transactions_items_widget.delete_item_button.clicked.connect(self._delete_transaction_item)

    def set_create_data(self, create_data: dict[str, str | int]) -> None:
        self._setup_create_data(create_data)
        self.transaction_info_widget.set_create_data(self.payment_text, self.customer,
                                                     self.document_number, self.address, self.notes)

    def _setup_create_data(self, create_data: dict[str, str | int]) -> None:
        self.payment_text = create_data.get("paymentText", "")
        self.payment_type = None
        self.customer_id = create_data.get("customerId", None)
        self.customer = create_data.get("customer", "")
        self.document_number = create_data.get("documentNumber", "")
        self.address = create_data.get("address", "")
        self.notes = create_data.get("notes", "")

    def _update_create_data(self) -> None:
        new_data = self.transactions_controller.create_transaction_data(self.transfer_type)
        if new_data is None:
            return
        self.set_create_data(new_data)

    def _add_transaction_item(self) -> None:
        new_item_data = self.transactions_controller.create_category_commodity_data(self.transfer_type)
        if new_item_data is None:
            return
        self.transactions_items_widget.add_item(new_item_data)

    def _update_transaction_item(self) -> None:
        index, item_data = self._get_item_data()
        if item_data:
            update_item_data = self.transactions_controller.update_category_commodity_data(item_data, self.transfer_type)
            if update_item_data is None:
                return
            self.transactions_items_widget.update_item(index, update_item_data)

    def _delete_transaction_item(self) -> None:
        index, item_data = self._get_item_data()
        informative_text = ""
        if item_data:
            informative_text = (
                f"{item_data["commodity"]}\n({item_data["unitCount"]}{item_data["commoditySuffix"]})"
            )
        question = MessageBoxes.show_question(self, "DELETE_TRANSACTION_ITEM", informative_text)
        if question:
            self.transactions_items_widget.delete_item(index)
            self.transactions_controller.on_item_deleted(self.transfer_type)

    def _get_item_data(self) -> tuple[QModelIndex | None, dict[str, str | int | float] | None]:
        index = self.transactions_items_widget.get_selected_index()
        if index is None or not index.isValid():
            return index, None
        data = self.transactions_items_widget.current_model.get_transaction_item_data(index)
        return index, data

    def return_transaction_data(self) -> dict[str, str | int] | None:
        if self.customer_id is None:
            return None
        return {
            "type": self.transfer_type,
            "customer_id": self.customer_id,
            "payment_type": self.payment_type,
            "notes": self.transaction_info_widget.get_notes()
        }

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        centre_dialog(self)