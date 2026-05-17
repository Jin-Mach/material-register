from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

from material_register.domain.category_dataclass import Category

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogTreeWidget(QTreeWidget):
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        super().__init__(catalog_widget)
        self.setHeaderHidden(True)

    def has_selection(self) -> bool:
        return self.selectionModel().hasSelection()

    def get_selected_category(self) -> int | None:
        item = self.currentItem()
        if item is None:
            return None
        return item.data(0, Qt.ItemDataRole.UserRole)

    def find_item_by_id(self, category_id: int) -> QTreeWidgetItem | None:
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            category = item.data(0, Qt.ItemDataRole.UserRole)
            if category and category.id == category_id:
                return item
        return None

    @staticmethod
    def create_category_item(category: Category) -> QTreeWidgetItem:
        item = QTreeWidgetItem([category.name])
        item.setData(0, Qt.ItemDataRole.UserRole, category)
        return item