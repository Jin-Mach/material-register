import pytest

from PySide6.QtWidgets import QWidget

from material_register.ui.dialogs.commodity_dialog import CommodityDialog
from material_register.ui.setup.ui_texts import UiTexts


class FakeCatalogWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.catalog_controller = FakeCatalogController()

# noinspection PyMethodMayBeStatic
class FakeCatalogController:
    def category_exists(self, name: str, ignored_id: int | None = None) -> bool:
        return False

# noinspection PyTypeChecker
@pytest.fixture
def dialog(qtbot):
    UiTexts.UI_TEXTS = {
        "CommodityDialog": {
            "categoryLabelText": "Category",
            "nameLabelText": "Name",
            "unitLabelText": "Unit",
            "defaultPriceLabelText": "Price",
            "activeLabelText": "Active",
            "notesLabelText": "Notes",
            "notesCountLabelText": "Count:",
            "saveButtonText": "Save",
            "closeButtonText": "Close"
        }
    }
    dialog = CommodityDialog(FakeCatalogWidget(), category_id=1, category_name="Test Category")
    qtbot.addWidget(dialog)
    return dialog

def test_commodity_valid(dialog):
    dialog.name_input.setText("Steel")
    dialog.unit_input.setText("kg")
    dialog.price_input.setText("10.5")
    dialog.notes_input.setText("notes")
    assert dialog._is_input_valid() is True
    data = dialog.get_commodity_data()
    assert data is not None
    assert data.name == "Steel"
    assert data.unit == "kg"
    assert data.default_price == 10.5
    assert data.notes == "notes"
    assert data.category_id == 1
    assert data.active == 1

def test_commodity_invalid_missing_fields(dialog):
    dialog.name_input.setText("")
    dialog.unit_input.setText("")
    dialog.price_input.setText("")
    assert dialog._is_input_valid() is False
    assert dialog.get_commodity_data() is None

def test_commodity_invalid_price(dialog):
    dialog.name_input.setText("Steel")
    dialog.unit_input.setText("kg")
    dialog.price_input.setText("abc")
    assert dialog._is_input_valid() is False