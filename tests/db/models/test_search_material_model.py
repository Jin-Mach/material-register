import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from material_register.db.config.model_constants import (
    MATERIAL_MODEL_COLUMNS_MAP,
    MATERIAL_MODELS_COLUMNS,
)
from material_register.db.models.search_models.search_material_model import (
    SearchMaterialModel,
)
from material_register.domain.search_dataclass import MaterialDataclass
from material_register.ui.config.styles_constants import INVENTORY_STOCK_STYLE


@pytest.fixture
def model() -> SearchMaterialModel:
    return SearchMaterialModel()


@pytest.fixture
def material_positive() -> MaterialDataclass:
    return MaterialDataclass(
        category_name="Metals",
        commodity_name="Copper",
        commodity_unit="kg",
        total=70.0,
    )


@pytest.fixture
def material_negative() -> MaterialDataclass:
    return MaterialDataclass(
        category_name="Plastics",
        commodity_name="PVC",
        commodity_unit="m",
        total=-10.0,
    )


def test_load_data(
    model: SearchMaterialModel,
    material_positive: MaterialDataclass,
    material_negative: MaterialDataclass,
) -> None:
    model.load_data([material_positive, material_negative])
    assert model.rowCount() == 2
    assert model.columnCount() == len(MATERIAL_MODELS_COLUMNS)


def test_get_columns_map() -> None:
    assert SearchMaterialModel.get_columns_map() == MATERIAL_MODEL_COLUMNS_MAP


def test_display_material_data(
    model: SearchMaterialModel, material_positive: MaterialDataclass
) -> None:
    model.load_data([material_positive])
    index_category = model.index(0, MATERIAL_MODEL_COLUMNS_MAP["category_name"])
    assert model.data(index_category, Qt.ItemDataRole.DisplayRole) == "Metals"
    index_commodity = model.index(0, MATERIAL_MODEL_COLUMNS_MAP["commodity_name"])
    assert model.data(index_commodity, Qt.ItemDataRole.DisplayRole) == "Copper"
    index_unit = model.index(0, MATERIAL_MODEL_COLUMNS_MAP["commodity_unit"])
    assert model.data(index_unit, Qt.ItemDataRole.DisplayRole) == "kg"
    index_total = model.index(0, MATERIAL_MODEL_COLUMNS_MAP["total"])
    assert model.data(index_total, Qt.ItemDataRole.DisplayRole) == "70.0 kg"


def test_display_negative_total(
    model: SearchMaterialModel, material_negative: MaterialDataclass
) -> None:
    model.load_data([material_negative])
    index = model.index(0, MATERIAL_MODEL_COLUMNS_MAP["total"])
    assert model.data(index, Qt.ItemDataRole.DisplayRole) == "-10.0 m"


def test_negative_total_color(
    model: SearchMaterialModel, material_negative: MaterialDataclass
) -> None:
    model.load_data([material_negative])
    index = model.index(0, MATERIAL_MODEL_COLUMNS_MAP["total"])
    assert model.data(index, Qt.ItemDataRole.ForegroundRole) == QColor(
        INVENTORY_STOCK_STYLE
    )


def test_positive_total_default_color(
    model: SearchMaterialModel, material_positive: MaterialDataclass
) -> None:
    model.load_data([material_positive])
    index = model.index(0, MATERIAL_MODEL_COLUMNS_MAP["total"])
    assert model.data(index, Qt.ItemDataRole.ForegroundRole) is None


def test_text_alignment(
    model: SearchMaterialModel, material_positive: MaterialDataclass
) -> None:
    model.load_data([material_positive])
    index_total = model.index(0, MATERIAL_MODEL_COLUMNS_MAP["total"])
    assert model.data(index_total, Qt.ItemDataRole.TextAlignmentRole) == (
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    )
    index_commodity = model.index(0, MATERIAL_MODEL_COLUMNS_MAP["commodity_name"])
    assert (
        model.data(index_commodity, Qt.ItemDataRole.TextAlignmentRole)
        == Qt.AlignmentFlag.AlignCenter
    )


def test_header_data(model: SearchMaterialModel) -> None:
    model.headers = {0: "Category", 1: "Material", 2: "Unit", 3: "Total"}
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Category"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Material"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Unit"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Total"


def test_load_empty_data(model: SearchMaterialModel) -> None:
    model.load_data([])
    assert model.rowCount() == 0
    assert model.columnCount() == len(MATERIAL_MODELS_COLUMNS)
