import pytest

from PySide6.QtWidgets import QWidget

from material_register.ui.dialogs.customer_dialog import CustomerDialog
from material_register.ui.setup.ui_texts import UiTexts


class FakeCustomersWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.customers_model = FakeCustomersModel()

# noinspection PyMethodMayBeStatic
class FakeCustomersModel:
    def document_exists(self, document: str, ignored_id: int | None = None) -> bool:
        return False

# noinspection PyTypeChecker
@pytest.fixture
def dialog(qtbot):
    UiTexts.UI_TEXTS = {
        "CustomerDialog": {
            "titleText": "Test",
            "subjectTypeItems": ["Individual", "Company"]
        }
    }
    dialog = CustomerDialog(FakeCustomersWidget())
    qtbot.addWidget(dialog)
    return dialog

def test_person_customer_valid(dialog):
    dialog.subject_type.setCurrentIndex(0)  # person
    dialog.first_name_input.setText("John")
    dialog.last_name_input.setText("Doe")
    dialog.document_type_input.setText("666")
    dialog.address_input.setText("Hell")
    assert dialog._is_input_valid(0) is True
    customer = dialog.get_customer_data()
    assert customer.company is None
    assert customer.first_name == "John"
    assert customer.last_name == "Doe"
    assert customer.document_number == "666"
    assert customer.address == "Hell"

def test_person_customer_invalid_missing_name(dialog):
    dialog.subject_type.setCurrentIndex(0)
    dialog.first_name_input.setText("")
    dialog.last_name_input.setText("")
    dialog.document_type_input.setText("666")
    dialog.address_input.setText("Hell")
    assert dialog._is_input_valid(0) is False
    assert dialog.get_customer_data() is None

def test_company_customer_valid(dialog):
    dialog.subject_type.setCurrentIndex(1)
    dialog.company_input.setText("ACME s.r.o.")
    dialog.document_type_input.setText("123")
    dialog.address_input.setText("Hell")
    assert dialog._is_input_valid(1) is True
    customer = dialog.get_customer_data()
    assert customer.company == "ACME s.r.o."
    assert customer.first_name is None
    assert customer.last_name is None