import pytest

from PySide6.QtCore import Qt

from material_register.db.config.model_constants import ITEM_MODEL_OUT_COLUMNS
from material_register.db.models.transaction_items_model_out import TransactionItemsModelOut


@pytest.fixture
def model() -> TransactionItemsModelOut:
    return TransactionItemsModelOut()

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
    assert model.columnCount() == len(ITEM_MODEL_OUT_COLUMNS)

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
    index_unit = model.index(0, ITEM_MODEL_OUT_COLUMNS.index("unitCount"))
    assert model.data(index_unit, Qt.ItemDataRole.DisplayRole) == "5 kg"
    index_category = model.index(0, ITEM_MODEL_OUT_COLUMNS.index("category"))
    assert model.data(index_category, Qt.ItemDataRole.DisplayRole) == "Food"

def test_display_unit_with_suffix(model, item) -> None:
    model.add_item(item)
    index = model.index(0, ITEM_MODEL_OUT_COLUMNS.index("unitCount"))
    value = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert value == "2 kg"

def test_return_total(model, item) -> None:
    model.add_item(item)
    assert model.return_total() == "2 kg"

def test_calculate_total_unit(model, item) -> None:
    model.add_item(item)
    total, suffix = model._calculate_total_unit()
    assert total == 2
    assert suffix == "kg"

def test_delete_item(model, item) -> None:
    model.add_item(item)
    assert model.rowCount() == 1
    index = model.index(0, 0)
    model.delete_item(index)
    assert model.rowCount() == 0

def test_get_transaction_item_data(model, item) -> None:
    model.add_item(item)
    index = model.index(0, 0)
    data = model.get_transaction_item_data(index)
    assert data["commodity"] == "Apple"
    assert data["unitCount"] == 2

def test_get_data(model, item) -> None:
    model.add_item(item)
    result = model.get_data()
    assert len(result) == 1
    assert result[0].commodityId == 1
    assert result[0].unitCount == 2
    assert result[0].pricePerUnit == 0