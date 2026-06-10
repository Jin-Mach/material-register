import pytest

from PySide6.QtCore import Qt

from material_register.db.config.model_constants import IN_MODEL_COLUMNS
from material_register.db.models.transaction_items_model_in import TransactionItemsModelIn


@pytest.fixture
def model() -> TransactionItemsModelIn:
    return TransactionItemsModelIn(price_suffix="£")

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

def test_update_item(model, item) -> None:
    model.add_item(item)
    updated_item = {
        "category": "Food",
        "commodity": "Apple",
        "commodityId": 1,
        "unitCount": 5,
        "pricePerUnit": 12,
        "commoditySuffix": "kg"
    }
    model.update_item(0, updated_item)
    index_unit = model.index(0, IN_MODEL_COLUMNS.index("unitCount"))
    assert model.data(index_unit, Qt.ItemDataRole.DisplayRole) == "5 kg"
    index_price = model.index(0, IN_MODEL_COLUMNS.index("pricePerUnit"))
    assert model.data(index_price, Qt.ItemDataRole.DisplayRole) == 12
    index_total = model.index(0, IN_MODEL_COLUMNS.index("totalPrice"))
    assert model.data(index_total, Qt.ItemDataRole.DisplayRole) == "60 £"

def test_total_price_calculation(model, item) -> None:
    model.add_item(item)
    assert model._calculate_total_price() == 20.0

def test_display_total_price(model, item) -> None:
    model.add_item(item)
    index = model.index(0, IN_MODEL_COLUMNS.index("totalPrice"))
    value = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert "20 £" in value

def test_display_unit_with_suffix(model, item) -> None:
    model.add_item(item)
    index = model.index(0, IN_MODEL_COLUMNS.index("unitCount"))
    value = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert value == "2 kg"