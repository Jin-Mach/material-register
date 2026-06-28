from typing import Any

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QColor
from PySide6.QtSql import QSqlQueryModel, QSqlDatabase

from material_register.db.config.model_constants import INVENTORY_COLUMNS_MAP
from material_register.db.config.queries_constants import INVENTORY_QUERY
from material_register.ui.helpers.styles import INVENTORY_STOCK_STYLE


class InventoryModel(QSqlQueryModel):
    def __init__(self, connection: QSqlDatabase) -> None:
        super().__init__()
        self.connection = connection

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if column == INVENTORY_COLUMNS_MAP["inventory_stock"]:
                stock = super().data(index, Qt.ItemDataRole.DisplayRole)
                unit_index = self.index(index.row(), INVENTORY_COLUMNS_MAP["commodity_unit"])
                unit = super().data(unit_index, Qt.ItemDataRole.DisplayRole)
                return f"{stock} {unit}"
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == INVENTORY_COLUMNS_MAP["inventory_stock"]:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.ForegroundRole:
            if column == INVENTORY_COLUMNS_MAP["inventory_stock"]:
                stock = super().data(index, Qt.ItemDataRole.DisplayRole)
                if isinstance(stock, float):
                    if stock < 0:
                        return QColor(INVENTORY_STOCK_STYLE)
        return super().data(index, role)

    def load_inventory_data(self) -> tuple[bool, str]:
        self.setQuery(INVENTORY_QUERY, self.connection)
        error = self.lastError()
        if error.isValid():
            return False, error.text()
        return True, ""