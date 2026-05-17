from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout

from material_register.ui.catalog.catalog_widgets.category_detail_widget import CategoryDetailWidget

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogDetailsWidget(QWidget):
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        super().__init__(catalog_widget)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.category_detail_widget = CategoryDetailWidget(self)
        main_layout.addWidget(self.category_detail_widget)
        main_layout.addStretch()
        return main_layout