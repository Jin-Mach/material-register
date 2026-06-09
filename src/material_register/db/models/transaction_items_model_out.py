from typing import Any

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QStandardItem, QStandardItemModel


class TransactionItemsModelOut(QStandardItemModel):
    COLUMNS = ["category", "commodity", "commodityId", "unitCount"]

    def __init__(self) -> None:
        super().__init__()
        self._setup_model()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        column = index.column()
        unit_column = self.COLUMNS.index("unitCount")
        if role == Qt.ItemDataRole.DisplayRole:
            if column == unit_column:
                value = self.data(index, Qt.ItemDataRole.UserRole)
                commodity_suffix = self.data(index, Qt.ItemDataRole.UserRole + 1)
                if value is None:
                    return ""
                return f"{value} {commodity_suffix}"
            return super().data(index, role)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        return super().data(index, role)

    def add_item(self, transaction_item: dict[str, str | int]) -> None:
        columns = ["category", "commodity", "commodityId", "unitCount"]
        items_list = []
        for key in columns:
            value = self._create_item(transaction_item[key])
            if key == "category":
                value.setData(transaction_item, Qt.ItemDataRole.UserRole)
            if key == "unitCount":
                value.setData(transaction_item["unitCount"], Qt.ItemDataRole.UserRole)
                value.setData(transaction_item["commoditySuffix"], Qt.ItemDataRole.UserRole + 1)
            items_list.append(value)
        self.appendRow(items_list)

    def update_item(self, row: int, data: dict[str, str | int]) -> None:
        for column, key in enumerate(self.COLUMNS):
            index = self.index(row, column)
            if key == "category":
                self.setData(index, data, Qt.ItemDataRole.UserRole)
                self.setData(index, data["category"], Qt.ItemDataRole.DisplayRole)
            elif key == "unitCount":
                self.setData(index, data["unitCount"], Qt.ItemDataRole.UserRole)
                self.setData(index, data["commoditySuffix"], Qt.ItemDataRole.UserRole + 1)
                self.setData(index, data["unitCount"], Qt.ItemDataRole.DisplayRole)
            else:
                self.setData(index, data[key], Qt.ItemDataRole.DisplayRole)

    def delete_item(self, index: QModelIndex) -> None:
        self.removeRow(index.row())

    def get_transaction_item_data(self, index: QModelIndex) -> dict[str, str | int]:
        return self.item(index.row(), 0).data(Qt.ItemDataRole.UserRole)

    def _setup_model(self) -> None:
        self.setColumnCount(len(self.COLUMNS))

    @staticmethod
    def _create_item(value: str) -> QStandardItem:
        return QStandardItem(str(value))

    @staticmethod
    def get_columns_map() -> dict[str, int]:
        return {
            "category": 0,
            "commodity": 1,
            "commodityId": 2,
            "unitCount": 3,
        }