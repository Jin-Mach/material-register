from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from material_register.db.config.model_constants import (
    SEARCH_MODEL_COLUMNS,
    SEARCH_MODEL_COLUMNS_MAP,
)
from material_register.domain.search_dataclass import SearchDataclass
from material_register.ui.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.utils.formatting_utils import (
    format_datetime_to_locale,
    format_number_to_locale,
)


class SearchTransactionsModel(QAbstractTableModel):
    def __init__(self) -> None:
        super().__init__()
        self._tooltip_texts = {}
        self.suffix = ""
        self.transaction_data = []
        self.headers = {}
        self.total_count = 0

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = Qt.ItemDataRole.DisplayRole
    ) -> Any:
        if not index.isValid():
            return None
        transaction = self.transaction_data[index.row()]
        column = SEARCH_MODEL_COLUMNS[index.column()]
        if role == Qt.ItemDataRole.DisplayRole:
            if column == "transaction_created_at":
                return format_datetime_to_locale(transaction.transaction_created_at)
            if column == "total":
                if transaction.transaction_type == TRANSFER_IN:
                    return f"{format_number_to_locale(transaction.total)} {self.suffix}"
                elif transaction.transaction_type == TRANSFER_OUT:
                    return f"{format_number_to_locale(transaction.total)} {transaction.suffix}"
            return getattr(transaction, column, None)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == "total":
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignCenter
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
        return len(self.transaction_data)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return len(SEARCH_MODEL_COLUMNS)

    def load_data(self, transactions: list[SearchDataclass]) -> None:
        self.beginResetModel()
        self.transaction_data = transactions
        self.endResetModel()
        self.total_count = len(self.transaction_data)

    @staticmethod
    def get_columns_map() -> dict[str, int]:
        return SEARCH_MODEL_COLUMNS_MAP
