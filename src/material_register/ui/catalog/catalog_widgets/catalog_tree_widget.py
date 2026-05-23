from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity
from material_register.services.error_handler import ErrorHandler

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogTreeWidget(QTreeWidget):
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        super().__init__(catalog_widget)
        self.setHeaderHidden(True)

    def reload_tree(self, categories: list[Category], commodities: list[Commodity]) -> None:
        self.blockSignals(True)
        self.setUpdatesEnabled(False)
        try:
            self.clear()
            for category in categories:
                category_item = QTreeWidgetItem([category.name])
                category_item.setData(0, Qt.ItemDataRole.UserRole, category)
                self.addTopLevelItem(category_item)
                for commodity in commodities:
                    if category.id == commodity.category_id:
                        item = QTreeWidgetItem(category_item)
                        item.setText(0, commodity.name)
                        item.setData(0, Qt.ItemDataRole.UserRole, commodity)
        except Exception as e:
            ErrorHandler.handle_error(e, "ui", "warning")
        finally:
            self.blockSignals(False)
            self.setUpdatesEnabled(True)

    def has_selection(self) -> bool:
        return self.selectionModel().hasSelection()

    def get_selected_data(self) -> tuple[Category | None, Commodity | None]:
        item = self.currentItem()
        if item is None:
            return None, None
        if item.parent() is None:
            return item.data(0, Qt.ItemDataRole.UserRole), None
        category_item = item.parent()
        return (category_item.data(0, Qt.ItemDataRole.UserRole),
                item.data(0, Qt.ItemDataRole.UserRole))

    def find_item_by_id(self, category_id: int) -> QTreeWidgetItem | None:
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            category = item.data(0, Qt.ItemDataRole.UserRole)
            if category and category.id == category_id:
                return item
        return None

    def create_commodity_item(self, commodity: Commodity) -> tuple[QTreeWidgetItem | None, QTreeWidgetItem | None]:
        category_id = commodity.category_id
        parent_item = self.find_item_by_id(category_id)
        if not parent_item:
            return None, None
        item = QTreeWidgetItem(parent_item)
        item.setText(0, commodity.name)
        item.setData(0, Qt.ItemDataRole.UserRole, commodity)
        parent_item.sortChildren(0, Qt.SortOrder.AscendingOrder)
        return parent_item, item

    @staticmethod
    def create_category_item(category: Category) -> QTreeWidgetItem:
        item = QTreeWidgetItem([category.name])
        item.setData(0, Qt.ItemDataRole.UserRole, category)
        return item