from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTreeWidget

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogTreeWidget(QTreeWidget):
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        super().__init__(catalog_widget)
        self.setHeaderHidden(True)