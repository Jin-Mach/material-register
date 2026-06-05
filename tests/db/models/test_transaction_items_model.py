import pytest

from PySide6.QtCore import Qt

from material_register.db.models.transaction_items_model import TransactionItemsModel


@pytest.fixture
def model() -> TransactionItemsModel:
    return TransactionItemsModel(price_suffix="£")

@pytest.fixture
def item() -> dict[str, str | int | float]:
    return {
        "category": "Food",
        "commodity": "Apple",
        "commodityId": 1,
        "unitCount": 2,
        "pricePerUnit": 10,
        "commoditySuffix": "kg"
    }

def test_add_item(model, item) -> None:
    model.add_item(item)
    assert model.rowCount() == 1
    assert model.columnCount() == 6

def test_total_price_calculation(model, item) -> None:
    model.add_item(item)
    assert model.total_count == 20.0

def test_display_total_price(model, item) -> None:
    model.add_item(item)
    index = model.index(0, model.COLUMNS.index("totalPrice"))
    value = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert "20 £" in value

def test_display_unit_with_suffix(model, item) -> None:
    model.add_item(item)
    index = model.index(0, model.COLUMNS.index("unitCount"))
    value = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert value == "2 kg"