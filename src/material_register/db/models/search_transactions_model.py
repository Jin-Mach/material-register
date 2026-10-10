import textwrap
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
        self._transaction_type_in_text = ""
        self._transaction_type_out_text = ""
        self._suffix = ""
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
            if column == "transaction_type":
                if transaction.transaction_type == TRANSFER_IN:
                    return self._transaction_type_in_text
                elif transaction.transaction_type == TRANSFER_OUT:
                    return self._transaction_type_out_text
            if column == "transaction_created_at":
                return format_datetime_to_locale(transaction.transaction_created_at)
            if column == "total":
                if transaction.transaction_type == TRANSFER_IN:
                    return (
                        f"{format_number_to_locale(transaction.total)} {self._suffix}"
                    )
                elif transaction.transaction_type == TRANSFER_OUT:
                    return f"{format_number_to_locale(transaction.total)} {transaction.suffix}"
            return getattr(transaction, column, None)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == "total":
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.ToolTipRole:
            if self._tooltip_texts:
                tooltip = SearchTransactionsModel._setup_tooltip(
                    transaction, self._tooltip_texts
                )
                if tooltip:
                    return tooltip
            return None
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

    def set_suffix(self, suffix: str) -> None:
        self._suffix = suffix

    def set_tooltip_texts(self, tooltip_texts: dict[str, str]) -> None:
        self._tooltip_texts = tooltip_texts

    def set_transaction_type_texts(self, type_in_text: str, type_out_text: str) -> None:
        self._transaction_type_in_text = type_in_text
        self._transaction_type_out_text = type_out_text

    @staticmethod
    def get_columns_map() -> dict[str, int]:
        return SEARCH_MODEL_COLUMNS_MAP

    @staticmethod
    def _setup_tooltip(
        transaction: SearchDataclass, tooltip_texts: dict[str, str]
    ) -> str:
        error_text = "N/A"
        type_text = tooltip_texts.get("type_text", "Type:")
        transaction_type = error_text
        if transaction.transaction_type == TRANSFER_IN:
            transaction_type = tooltip_texts.get("IN", error_text)
        if transaction.transaction_type == TRANSFER_OUT:
            transaction_type = tooltip_texts.get("OUT", error_text)
        customer_text = tooltip_texts.get("customer_text", "Customer:")
        customer_name = transaction.customer_name or error_text
        address_text = tooltip_texts.get("address_text", "Address:")
        customer_address = transaction.customer_address or error_text
        payment_text = tooltip_texts.get("payment_text", "Payment:")
        payment_type = tooltip_texts.get(transaction.payment_type, error_text)
        notes_text = tooltip_texts.get("notes_text", "Notes:")
        notes = transaction.transaction_notes or error_text
        tooltip = (
            f"{type_text} {transaction_type}\n"
            f"{customer_text} {customer_name}\n"
            f"{address_text} {customer_address}"
        )
        if transaction.transaction_type == TRANSFER_IN:
            tooltip += f"\n{payment_text} {payment_type}"
        if notes != error_text:
            wrapped_notes = textwrap.fill(
                notes,
                width=50,
                initial_indent="    ",
                subsequent_indent="    ",
            )
            tooltip += f"\n{notes_text}\n{wrapped_notes}"
        return tooltip
