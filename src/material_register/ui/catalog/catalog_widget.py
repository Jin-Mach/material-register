from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QHBoxLayout

from material_register.ui.catalog.catalog_widgets.catalog_details_widget import CatalogDetailsWidget
from material_register.ui.catalog.catalog_widgets.catalog_tree_widget import CatalogTreeWidget

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class CatalogWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        self.tree_widget = CatalogTreeWidget(self)
        self.details_widget = CatalogDetailsWidget(self)
        main_layout.addWidget(self.tree_widget)
        main_layout.addWidget(self.details_widget)
        return main_layout