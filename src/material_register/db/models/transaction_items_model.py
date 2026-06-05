from typing import Any

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QStandardItemModel, QStandardItem


class TransactionItemsModel(QStandardItemModel):
    COLUMNS = ["category", "commodity", "commodityId", "unitCount", "pricePerUnit", "totalPrice"]

    def __init__(self, price_suffix: str) -> None:
        super().__init__()
        self.price_suffix = price_suffix
        self.total_count = 0.0
        self._setup_model()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        column = index.column()
        total_column = self.COLUMNS.index("totalPrice")
        if role == Qt.ItemDataRole.DisplayRole:
            if column == total_column:
                value = self.data(index, Qt.ItemDataRole.UserRole)
                if value is None:
                    return ""
                return f"{value} {self.price_suffix}"
            if column == self.COLUMNS.index("unitCount"):
                value = self.data(index, Qt.ItemDataRole.UserRole)
                commodity_suffix = self.data(index, Qt.ItemDataRole.UserRole + 1)
                if value is None:
                    return ""
                return f"{value} {commodity_suffix}"
            return super().data(index, role)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == total_column:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignCenter
        return super().data(index, role)

    def add_item(self, transaction_item: dict[str, str | int | float]) -> None:
        columns = ["category", "commodity", "commodityId", "unitCount", "pricePerUnit"]
        items_list = []
        for key in columns:
            value = TransactionItemsModel._create_item(transaction_item[key])
            if key == "unitCount":
                value.setData(transaction_item["commoditySuffix"], Qt.ItemDataRole.UserRole + 1)
            items_list.append(value)
        total = self._get_total_count(transaction_item["unitCount"], transaction_item["pricePerUnit"])
        items_list.append(total)
        self.appendRow(items_list)

    def return_total_price(self) -> str:
        return f"{self.total_count} {self.price_suffix}"

    def _setup_model(self) -> None:
        self.setColumnCount(len(self.COLUMNS))

    def _get_total_count(self, unit: int | float, price_per_unit: int | float) -> QStandardItem:
        total = round(unit * price_per_unit, 2)
        self.total_count += total
        item = QStandardItem(str(total))
        item.setData(total, Qt.ItemDataRole.UserRole)
        return item

    @staticmethod
    def get_columns_map() -> dict[str, int]:
        return {"category": 0,
                "commodity": 1,
                "commodityId": 2,
                "unitCount": 3,
                "pricePerUnit": 4,
                "totalPrice": 5
                }

    @staticmethod
    def _create_item(value: str) -> QStandardItem:
        item = QStandardItem(str(value))
        item.setData(value, Qt.ItemDataRole.UserRole)
        return item