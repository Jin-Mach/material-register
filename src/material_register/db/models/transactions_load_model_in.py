from typing import Any
from datetime import datetime

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtSql import QSqlDatabase

from material_register.db.config.model_constants import LOAD_MODEL_IN_COLUMNS
from material_register.db.queries.transactions_load_queries import TransactionsLoadQueries
from material_register.domain.transaction_dataclass import Transaction


class TransactionsLoadModelIn(QAbstractTableModel):
    def __init__(self, db_connection: QSqlDatabase) -> None:
        super().__init__()
        self.db_connection = db_connection
        self.suffix = ""
        self.transaction_data = []
        self.headers = {}
        self.total_count = 0

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        transaction = self.transaction_data[index.row()]
        column = LOAD_MODEL_IN_COLUMNS[index.column()]
        if role == Qt.ItemDataRole.DisplayRole:
            if column == "transaction_created_at":
                return TransactionsLoadModelIn._format_datetime(transaction.transaction_created_at)
            if column == "total":
                return f"{transaction.total} {self.suffix}"
            return getattr(transaction, column, None)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == "total":
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.UserRole:
            if column == "transaction_created_at":
                return TransactionsLoadModelIn._format_datetime(transaction.transaction_created_at)
            if column == "total":
                return float(transaction.total)
            parts_list = []
            for part in (transaction.company_normalized, transaction.first_name_normalized,
                         transaction.last_name_normalized, transaction.customer_document_number,
                         transaction.address_normalized):
                if part:
                    parts_list.append(part)
            return " ".join(parts_list).lower()
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.headers.get(section)
        return super().headerData(section, orientation, role)

    def rowCount(self, parent=QModelIndex()) -> int:
        if not self.transaction_data:
            return 0
        return len(self.transaction_data)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(LOAD_MODEL_IN_COLUMNS)

    def removeRows(self, row: int, count: int = 1, parent=QModelIndex()) -> bool:
        self.beginRemoveRows(parent, row, row + count - 1)
        del self.transaction_data[row:row + count]
        self.endRemoveRows()
        return True

    def load_transactions_data(self) -> list[Transaction]:
        self.beginResetModel()
        self.transaction_data = TransactionsLoadQueries.load_transaction_in(self.db_connection)
        self.endResetModel()
        self.total_count = len(self.transaction_data)
        return self.transaction_data

    def set_basic_filter(self, filtered_data: list[Transaction]) -> None:
        self.beginResetModel()
        self.transaction_data = filtered_data
        self.endResetModel()

    def set_suffix(self, suffix: str) -> None:
        self.suffix = suffix

    @staticmethod
    def _format_datetime(created: str) -> str:
        date = datetime.fromisoformat(created)
        return date.strftime("%d.%m.%Y")