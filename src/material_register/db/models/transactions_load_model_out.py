import textwrap
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtSql import QSqlDatabase

from material_register.db.config.model_constants import LOAD_MODEL_IN_COLUMNS
from material_register.db.queries.transactions_load_queries import (
    TransactionsLoadQueries,
)
from material_register.domain.transaction_dataclass import Transaction
from material_register.ui.helpers.formating_utils import (
    format_datetime_to_locale,
    format_number_to_locale,
)


class TransactionsLoadModelOut(QAbstractTableModel):
    def __init__(self, db_connection: QSqlDatabase) -> None:
        super().__init__()
        self.db_connection = db_connection
        self.tooltip_texts = {}
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
                return format_datetime_to_locale(transaction.transaction_created_at)
            if column == "total":
                return (
                    f"{format_number_to_locale(transaction.total)} {transaction.suffix}"
                )
            return getattr(transaction, column, None)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == "total":
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.ToolTipRole:
            if self.tooltip_texts:
                tooltip = TransactionsLoadModelOut._setup_tooltip(
                    transaction, self.tooltip_texts
                )
                if tooltip:
                    return tooltip
            return None
        if role == Qt.ItemDataRole.UserRole:
            if column == "transaction_created_at":
                return format_datetime_to_locale(transaction.transaction_created_at)
            if column == "total":
                return float(transaction.total)
            parts_list = []
            for part in (
                transaction.company_normalized,
                transaction.first_name_normalized,
                transaction.last_name_normalized,
                transaction.customer_document_number,
                transaction.address_normalized,
            ):
                if part:
                    parts_list.append(part)
            return " ".join(parts_list).lower()
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if (
            orientation == Qt.Orientation.Horizontal
            and role == Qt.ItemDataRole.DisplayRole
        ):
            return self.headers.get(section)
        return super().headerData(section, orientation, role)

    def rowCount(self, parent=None) -> int:
        return len(self.transaction_data)

    def columnCount(self, parent=None) -> int:
        return len(LOAD_MODEL_IN_COLUMNS)

    def removeRows(self, row: int, count: int = 1, parent=None) -> bool:
        if parent is None:
            parent = QModelIndex()
        self.beginRemoveRows(parent, row, row + count - 1)
        del self.transaction_data[row : row + count]
        self.endRemoveRows()
        return True

    def load_transactions_data(self) -> list[Transaction]:
        self.beginResetModel()
        self.transaction_data = TransactionsLoadQueries.load_transactions_out(
            self.db_connection
        )
        self.endResetModel()
        self.total_count = len(self.transaction_data)
        return self.transaction_data

    def set_basic_filter(self, filtered_data: list[Transaction]) -> None:
        self.beginResetModel()
        self.transaction_data = filtered_data
        self.endResetModel()

    def set_tooltip_texts(self, tooltip_texts: dict[str, str]) -> None:
        self.tooltip_texts = tooltip_texts

    @staticmethod
    def _setup_tooltip(transaction: Transaction, tooltip_texts: dict[str, str]) -> str:
        error_text = "N/A"
        customer_text = tooltip_texts.get("customer_text", "Customer:")
        customer_name = transaction.customer_name or error_text
        address_text = tooltip_texts.get("address_text", "Address:")
        customer_address = transaction.customer_address or error_text
        notes_text = tooltip_texts.get("notes_text", "Notes:")
        notes = transaction.transaction_notes or error_text
        tooltip = f"{customer_text} {customer_name}\n{address_text} {customer_address}"
        if notes != error_text:
            wrapped_notes = textwrap.fill(
                notes,
                width=50,
                initial_indent="    ",
                subsequent_indent="    ",
            )
            tooltip += f"\n{notes_text}\n{wrapped_notes}"
        return tooltip
