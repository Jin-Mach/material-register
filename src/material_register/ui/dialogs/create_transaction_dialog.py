from typing import TYPE_CHECKING

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QShowEvent, Qt, QRegularExpressionValidator
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, \
    QSizePolicy, QHBoxLayout, QCompleter, QWidget

from material_register.config.app_constants import PAYMENT_VALUES, TRANSFER_OUT, TRANSFER_IN
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.styles import INVALID_INPUT_STYLE
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget
    from material_register.db.models.customers_completer_model import CustomersCompleterModel


# noinspection PyTypeChecker
class CreateTransactionDialog(QDialog):
    def __init__(self, transactions_widget: "TransactionsWidget", completer_model: "CustomersCompleterModel", transfer_type: str) -> None:
        super().__init__(transactions_widget)
        self.completer_model = completer_model
        self.transfer_type = transfer_type
        self.selected_customer = None
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._setup_completer(self.completer_model)
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        type_layout = QHBoxLayout()
        type_form_layout = QFormLayout()
        self.payment_type_label = QLabel()
        self.payment_type_label.setObjectName("paymentTypeLabel")
        self.payment_type_combobox = QComboBox()
        self.payment_type_combobox.setObjectName("paymentTypeCombobox")
        customer_form_layout = QFormLayout()
        self.customer_name_label = QLabel()
        self.customer_name_label.setObjectName("customerNameLabel")
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setObjectName("customerNameInput")
        self.customer_name_input.setMinimumWidth(300)
        self.customer_name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.customer_document_number_label = QLabel()
        self.customer_document_number_label.setObjectName("customerDocumentNumberLabel")
        self.customer_document_number = QLabel()
        self.customer_address_label = QLabel()
        self.customer_address_label.setObjectName("customerAddressLabel")
        self.customer_address = QLabel()
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.continue_transaction_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.continue_transaction_button.setObjectName("continueTransactionButton")
        self.cancel_transaction_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_transaction_button.setObjectName("cancelTransactionButton")
        type_form_layout.addRow(self.payment_type_label, self.payment_type_combobox)
        customer_form_layout.addRow(self.customer_name_label, self.customer_name_input)
        customer_form_layout.addRow(self.customer_document_number_label, self.customer_document_number)
        customer_form_layout.addRow(self.customer_address_label, self.customer_address)
        type_layout.addStretch()
        type_layout.addLayout(type_form_layout)
        type_layout.addStretch()
        main_layout.addLayout(type_layout)
        main_layout.addLayout(customer_form_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [self.payment_type_label, self.customer_name_label,
                   self.customer_document_number_label, self.customer_address_label,
                   self.continue_transaction_button, self.cancel_transaction_button]
        self._setup_texts(widgets)
        self._set_validators()
        self._set_required_style()
        self._update_continue_button_state()
        self._apply_transfer_type()

    def _create_connection(self) -> None:
        self.continue_transaction_button.clicked.connect(self.accept)
        self.cancel_transaction_button.clicked.connect(self.reject)
        self.completer.activated.connect(self._on_customer_selected)
        self.customer_name_input.textEdited.connect(self._customer_name_edited)

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_items(self) -> None:
        payment_values = PAYMENT_VALUES
        texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        payment_items = texts.get(f"{self.payment_type_combobox.objectName()}Items", ["Cash", "Transfer"])
        for text, value in zip(payment_items, payment_values):
            self.payment_type_combobox.addItem(text, value)

    def _set_validators(self) -> None:
        customer_validator = QRegularExpressionValidator(QRegularExpression(r"^[\p{L}0-9 .,&\-]{1,50}$"))
        self.customer_name_input.setValidator(customer_validator)

    def _apply_transfer_type(self) -> None:
        if self.transfer_type == TRANSFER_OUT:
            self.payment_type_label.hide()
            self.payment_type_combobox.hide()
            return
        self._setup_items()

    def _set_dialog_size(self, width: int = 500) -> None:
        self.setFixedWidth(width)
        self.adjustSize()
        self.setFixedSize(width, self.size().height())

    def _setup_completer(self, completer_model: "CustomersCompleterModel") -> None:
        self.completer = QCompleter()
        self.completer.setModel(completer_model)
        self.completer.setCompletionRole(Qt.ItemDataRole.UserRole + 10)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.customer_name_input.setCompleter(self.completer)

    def _on_customer_selected(self, text: str) -> None:
        customer = self.completer_model.get_customer_by_text(text)
        if customer is None:
            return
        self.selected_customer = customer
        self.customer_document_number.setText(self.selected_customer.document_number)
        self.customer_address.setText(self.selected_customer.address)
        self._set_required_style()
        self._update_continue_button_state()

    def _customer_name_edited(self) -> None:
        self.selected_customer = None
        self.customer_document_number.clear()
        self.customer_address.clear()
        self._set_required_style()
        self._update_continue_button_state()

    def _update_continue_button_state(self) -> None:
        self.continue_transaction_button.setEnabled(self.selected_customer is not None)

    def _set_required_style(self) -> None:
        if self.selected_customer is None:
            self.customer_name_input.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            self.customer_name_input.setStyleSheet("")

    def get_create_data(self) -> dict[str, str | int | None] | None:
        if self.selected_customer is None:
            return None
        payment_type = "NONE"
        if self.transfer_type == TRANSFER_IN:
            payment_type = self.payment_type_combobox.currentData()
        return {
            "paymentType": payment_type,
            "customerId": self.selected_customer.id,
            "customer": self.customer_name_input.text().strip(),
            "documentNumber": self.customer_document_number.text(),
            "address": self.customer_address.text()
        }

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._set_dialog_size()