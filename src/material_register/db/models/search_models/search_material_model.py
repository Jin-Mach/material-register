from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from material_register.db.config.model_constants import (
    MATERIAL_MODEL_COLUMNS_MAP,
    MATERIAL_MODELS_COLUMNS,
)
from material_register.domain.search_dataclass import MaterialDataclass
from material_register.ui.config.styles_constants import INVENTORY_STOCK_STYLE
from material_register.utils.formatting_utils import format_number_to_locale


class SearchMaterialModel(QAbstractTableModel):
    def __init__(self) -> None:
        super().__init__()
        self.material_data = []
        self.headers = {}

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if not index.isValid():
            return None
        material = self.material_data[index.row()]
        column = MATERIAL_MODELS_COLUMNS[index.column()]
        if role == Qt.ItemDataRole.DisplayRole:
            if column == "category_name":
                return material.category_name
            if column == "commodity_name":
                return material.commodity_name
            if column == "commodity_unit":
                return material.commodity_unit
            if column == "total":
                return f"{format_number_to_locale(material.total)} {material.commodity_unit}"
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == "total":
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.ForegroundRole:  # noqa: SIM102
            if column == "total" and material.total < 0:
                return QColor(INVENTORY_STOCK_STYLE)
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self.headers.get(section)
        return super().headerData(section, orientation, role)

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self.material_data)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return len(MATERIAL_MODELS_COLUMNS)

    def load_data(self, materials: list[MaterialDataclass]) -> None:
        self.beginResetModel()
        self.material_data = materials
        self.endResetModel()

    @staticmethod
    def get_columns_map() -> dict[str, int]:
        return MATERIAL_MODEL_COLUMNS_MAP
