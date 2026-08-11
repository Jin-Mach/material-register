import pytest
from PySide6.QtWidgets import QWidget

from material_register.ui.dialogs.category_dialog import CategoryDialog
from material_register.ui.setup.ui_texts import UiTexts


# noinspection PyMethodMayBeStatic
class FakeCatalogController:
    def category_exists(self, name: str, ignored_id: int | None = None) -> bool:
        return False


class FakeCatalogWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.catalog_controller = FakeCatalogController()


# noinspection PyTypeChecker
@pytest.fixture
def dialog(qtbot) -> CategoryDialog:
    UiTexts.UI_TEXTS = {
        "CategoryDialog": {
            "categoryNameLabelText": "Name",
            "notesLabelText": "Notes",
            "notesCountLabelText": "Count:",
            "saveButtonText": "Save",
            "closeButtonText": "Close",
        }
    }
    dialog = CategoryDialog(FakeCatalogWidget())
    qtbot.addWidget(dialog)
    return dialog


def test_category_valid(dialog: CategoryDialog) -> None:
    dialog.category_name_input.setText("Hardware")
    dialog.notes_input.setText("Test notes")
    assert dialog._is_input_valid() is True
    assert dialog._is_category_valid() is True
    data = dialog.get_category_data()
    assert data is not None
    assert data.name == "Hardware"
    assert data.notes == "Test notes"


def test_category_invalid_empty_name(dialog: CategoryDialog) -> None:
    dialog.category_name_input.setText("")
    dialog.notes_input.setText("Some notes")
    assert dialog._is_input_valid() is False
    assert dialog.get_category_data() is None


def test_category_invalid_duplicate(dialog: CategoryDialog) -> None:
    dialog.catalog_widget.catalog_controller.category_exists = (
        lambda name, ignored_id=None: True
    )
    dialog.category_name_input.setText("Hardware")
    assert dialog._is_category_valid() is False
