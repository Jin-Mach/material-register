from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

from material_register.db.config.model_constants import INVENTORY_HISTORY_MODEL_COLUMNS
from material_register.ui.config.styles_constants import INVENTORY_STOCK_STYLE
from material_register.utils.formatting_utils import (
    format_number_to_locale,
    format_sql_date_to_locale,
)


class InventoryHistoryModel(QAbstractTableModel):
    def __init__(self) -> None:
        super().__init__()
        self.history_data = []
        self.commodity_unit = ""

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if not index.isValid():
            return None
        history_value = self.history_data[index.row()][index.column()]
        column = INVENTORY_HISTORY_MODEL_COLUMNS[index.column()]
        if role == Qt.ItemDataRole.DisplayRole:
            if column == "history_date":
                return format_sql_date_to_locale(history_value)
            if column == "date_total":
                return f"{format_number_to_locale(history_value)} {self.commodity_unit}"
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == "history_date":
                return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            if column == "date_total":
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        if (
            role == Qt.ItemDataRole.ForegroundRole
            and column == "date_total"
            and history_value < 0
        ):
            return QColor(INVENTORY_STOCK_STYLE)
        return None

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        return len(self.history_data)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return len(INVENTORY_HISTORY_MODEL_COLUMNS)

    def load_data(
        self, history_data: list[list[str | float]], commodity_unit: str
    ) -> None:
        self.beginResetModel()
        self.history_data = history_data
        self.commodity_unit = commodity_unit
        self.endResetModel()
