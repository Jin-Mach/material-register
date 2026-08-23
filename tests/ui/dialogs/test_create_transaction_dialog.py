import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from material_register.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.domain.customers_dataclass import Customer
from material_register.ui.dialogs.create_transaction_dialog import (
    CreateTransactionDialog,
)
from material_register.ui.setup.ui_texts import UiTexts


class FakeCustomersCompleterModel(QStandardItemModel):
    def __init__(self, customer: Customer) -> None:
        super().__init__()
        item = QStandardItem(f"{customer.company} - {customer.address}")
        item.setData(customer.company, Qt.ItemDataRole.UserRole + 10)
        item.setData(customer, Qt.ItemDataRole.UserRole)
        self.appendRow(item)

    def get_customer_by_text(self, text: str) -> Customer | None:
        for row in range(self.rowCount()):
            index = self.index(row, 0)
            if self.data(index, Qt.ItemDataRole.UserRole + 10) == text:
                return self.data(index, Qt.ItemDataRole.UserRole)
        return None


@pytest.fixture
def ui_texts() -> None:
    UiTexts.UI_TEXTS = {
        "CreateTransactionDialog": {
            "paymentTypeLabelText": "Payment type",
            "customerNameLabelText": "Customer",
            "customerDocumentNumberLabelText": "Document number",
            "customerAddressLabelText": "Address",
            "continueTransactionButtonText": "Continue",
            "cancelTransactionButtonText": "Cancel",
            "paymentTypeComboboxItems": ["Cash", "Transfer"],
        }
    }


# noinspection PyTypeChecker
@pytest.fixture
def dialog(qtbot, ui_texts) -> CreateTransactionDialog:
    customer = Customer(
        id=7,
        company="Acme s.r.o.",
        document_number="ABC-123",
        address="Prague",
    )
    dialog = CreateTransactionDialog(
        None,
        FakeCustomersCompleterModel(customer),
        TRANSFER_IN,
    )
    qtbot.addWidget(dialog)
    return dialog


def test_create_transaction_dialog_requires_customer(
    dialog: CreateTransactionDialog,
) -> None:
    assert dialog.continue_transaction_button.isEnabled() is False
    assert dialog.get_create_data() is None


def test_create_transaction_dialog_selects_customer(
    dialog: CreateTransactionDialog,
) -> None:
    dialog.customer_name_input.setText("Acme s.r.o.")
    dialog._on_customer_selected("Acme s.r.o.")

    assert dialog.selected_customer is not None
    assert dialog.selected_customer.id == 7
    assert dialog.customer_document_number.text() == "ABC-123"
    assert dialog.customer_address.text() == "Prague"
    assert dialog.continue_transaction_button.isEnabled() is True

    data = dialog.get_create_data()
    assert data is not None
    assert data["paymentType"] == "CASH"
    assert data["customerId"] == 7
    assert data["customer"] == "Acme s.r.o."
    assert data["documentNumber"] == "ABC-123"
    assert data["address"] == "Prague"


def test_create_transaction_dialog_clears_selection_on_edit(
    dialog: CreateTransactionDialog,
) -> None:
    dialog.customer_name_input.setText("Acme s.r.o.")
    dialog._on_customer_selected("Acme s.r.o.")

    dialog._customer_name_edited()

    assert dialog.selected_customer is None
    assert dialog.customer_document_number.text() == ""
    assert dialog.customer_address.text() == ""
    assert dialog.continue_transaction_button.isEnabled() is False


# noinspection PyTypeChecker
def test_create_transaction_dialog_out_transfer_hides_payment_type(qtbot) -> None:
    customer = Customer(
        id=13,
        company="Beta",
        document_number="XYZ-999",
        address="Brno",
    )
    UiTexts.UI_TEXTS = {
        "CreateTransactionDialog": {
            "paymentTypeLabelText": "Payment type",
            "customerNameLabelText": "Customer",
            "customerDocumentNumberLabelText": "Document number",
            "customerAddressLabelText": "Address",
            "continueTransactionButtonText": "Continue",
            "cancelTransactionButtonText": "Cancel",
        }
    }
    dialog = CreateTransactionDialog(
        None,
        FakeCustomersCompleterModel(customer),
        TRANSFER_OUT,
    )
    qtbot.addWidget(dialog)

    assert dialog.payment_type_label.isHidden() is True
    assert dialog.payment_type_combobox.isHidden() is True

    dialog.customer_name_input.setText("Beta")
    dialog._on_customer_selected("Beta")
    data = dialog.get_create_data()

    assert data is not None
    assert data["paymentType"] == "NONE"
    assert data["customerId"] == 13
