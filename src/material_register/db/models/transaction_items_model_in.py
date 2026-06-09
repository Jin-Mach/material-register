from typing import Any

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QStandardItem, QStandardItemModel

from material_register.config.app_maps import IN_MODEL_COLUMNS


class TransactionItemsModelIn(QStandardItemModel):
    def __init__(self, price_suffix: str) -> None:
        super().__init__()
        self.price_suffix = price_suffix
        self._setup_model()

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        column = index.column()
        total_column = IN_MODEL_COLUMNS.index("totalPrice")
        if role == Qt.ItemDataRole.DisplayRole:
            if column == total_column:
                value = self.data(index, Qt.ItemDataRole.UserRole)
                if value is None:
                    return ""
                return f"{value} {self.price_suffix}"
            if column == IN_MODEL_COLUMNS.index("unitCount"):
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
            value = TransactionItemsModelIn._create_item(transaction_item[key])
            if key == "category":
                value.setData(transaction_item, Qt.ItemDataRole.UserRole)
            if key == "unitCount":
                value.setData(transaction_item["unitCount"], Qt.ItemDataRole.UserRole)
                value.setData(transaction_item["commoditySuffix"], Qt.ItemDataRole.UserRole + 1)
            items_list.append(value)
        total = TransactionItemsModelIn.get_item_total_count(transaction_item["unitCount"], transaction_item["pricePerUnit"])
        items_list.append(total)
        self.appendRow(items_list)

    def update_item(self, row: int, data: dict[str, str | int | float]) -> None:
        for column, key in enumerate(IN_MODEL_COLUMNS):
            index = self.index(row, column)
            if key == "category":
                self.setData(index, data, Qt.ItemDataRole.UserRole)
                self.setData(index, data["category"], Qt.ItemDataRole.DisplayRole)
            elif key == "unitCount":
                self.setData(index, data["unitCount"], Qt.ItemDataRole.UserRole)
                self.setData(index, data["commoditySuffix"], Qt.ItemDataRole.UserRole + 1)
                self.setData(index, data["unitCount"], Qt.ItemDataRole.DisplayRole)
            elif key == "totalPrice":
                total = self._calculate_total_count(data["unitCount"], data["pricePerUnit"])
                self.setData(index, total, Qt.ItemDataRole.UserRole)
                self.setData(index, total, Qt.ItemDataRole.DisplayRole)
            else:
                self.setData(index, data[key], Qt.ItemDataRole.DisplayRole)

    def delete_item(self, index: QModelIndex) -> None:
        self.removeRow(index.row())

    def return_total_price(self) -> str:
        total_count = self._calculate_total_price()
        return f"{total_count} {self.price_suffix}"

    def get_transaction_item_data(self, index: QModelIndex) -> dict[str, str | int | float]:
        return self.item(index.row(), 0).data(Qt.ItemDataRole.UserRole)

    def _calculate_total_price(self) -> float:
        total_count = 0.0
        for row in range(self.rowCount()):
            item_data = self.item(row, 0).data(Qt.ItemDataRole.UserRole)
            total_count += item_data["unitCount"] * item_data["pricePerUnit"]
        return round(total_count, 2)

    def _setup_model(self) -> None:
        self.setColumnCount(len(IN_MODEL_COLUMNS))

    @staticmethod
    def get_item_total_count(unit: int | float, price_per_unit: int | float) -> QStandardItem:
        total = TransactionItemsModelIn._calculate_total_count(unit, price_per_unit)
        item = QStandardItem(str(total))
        item.setData(total, Qt.ItemDataRole.UserRole)
        return item

    @staticmethod
    def _calculate_total_count(unit: int | float, price_per_unit: int | float) -> float:
        return round(unit * price_per_unit, 2)

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
        return item