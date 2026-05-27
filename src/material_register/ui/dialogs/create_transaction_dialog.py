from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QFormLayout, QLabel, QLineEdit, QDialogButtonBox, \
    QSizePolicy, QHBoxLayout

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


# noinspection PyTypeChecker
class CreateTransactionDialog(QDialog):
    def __init__(self, transactions_widget: "TransactionsWidget") -> None:
        super().__init__(transactions_widget)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        type_layout = QHBoxLayout()
        type_form_layout = QFormLayout()
        self.transaction_type_label = QLabel("Transaction:")
        self.transaction_type_label.setObjectName("transactionTypeLabel")
        self.transaction_type_combobox = QComboBox()
        self.transaction_type_combobox.setObjectName("transactionTypeCombobox")
        self.payment_label = QLabel("Payment")
        self.payment_label.setObjectName("paymentLabel")
        self.payment_combobox = QComboBox()
        self.payment_combobox.setObjectName("paymentCombobox")
        customer_form_layout = QFormLayout()
        self.customer_name_label = QLabel("Customer:")
        self.customer_name_label.setObjectName("customerNameLabel")
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setObjectName("customerNameInput")
        self.customer_name_input.setMinimumWidth(300)
        self.customer_name_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.customer_document_number_label = QLabel("Document:")
        self.customer_document_number_label.setObjectName("customerDocumentNumberLabel")
        self.customer_document_number = QLabel("document number (max 30 letters)")
        self.customer_address_label = QLabel("Address:")
        self.customer_address_label.setObjectName("customerAddressLabel")
        self.customer_address = QLabel("very long address (max 50 letters)....")
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.continue_transaction_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.continue_transaction_button.setObjectName("continueTransactionButton")
        self.cancel_transaction_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_transaction_button.setObjectName("cancelTransactionButton")
        type_form_layout.addRow(self.transaction_type_label, self.transaction_type_combobox)
        type_form_layout.addRow(self.payment_label, self.payment_combobox)
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
        self.transaction_type_combobox.addItem("In", "IN")
        self.transaction_type_combobox.addItem("Out", "OUT")
        self.payment_combobox.addItem("Cash", "CASH")
        self.payment_combobox.addItem("Transfer", "TRANSFER")

    def _create_connection(self) -> None:
        self.continue_transaction_button.clicked.connect(self.accept)
        self.cancel_transaction_button.clicked.connect(self.reject)

    def _set_dialog_size(self, width: int = 500) -> None:
        self.setFixedWidth(width)
        self.adjustSize()
        self.setFixedSize(width, self.size().height())

    def get_transaction_data(self) -> dict[str, str]:
        return {
            "transactionType": self.transaction_type_combobox.currentData(),
            "payment": self.payment_combobox.currentData(),
            "customer": self.customer_name_input.text().strip(),
            "documentNumber": self.customer_document_number_label.text(),
            "address": self.customer_address_label.text()
        }

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._set_dialog_size()