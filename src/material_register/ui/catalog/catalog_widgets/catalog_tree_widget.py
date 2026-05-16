from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogTreeWidget(QTreeWidget):
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        super().__init__(catalog_widget)
        self.setHeaderHidden(True)

    def has_selection(self) -> bool:
        return self.selectionModel().hasSelection()

    def get_selected_id(self) -> int | None:
        item = self.currentItem()
        if item is None:
            return None
        return item.data(0, Qt.ItemDataRole.UserRole)