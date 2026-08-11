from typing import TYPE_CHECKING

from PySide6.QtWidgets import QVBoxLayout, QWidget

from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity
from material_register.ui.catalog.catalog_widgets.category_detail_widget import (
    CategoryDetailWidget,
)
from material_register.ui.catalog.catalog_widgets.commodities_grid_widget import (
    CommoditiesGridWidget,
)

if TYPE_CHECKING:
    from material_register.controllers.catalog_controller import CatalogController
    from material_register.ui.catalog.catalog_widgets.catalog_details_widget import (
        CatalogDetailsWidget,
    )


class CategoryWithCommoditiesWidget(QWidget):
    def __init__(self, catalog_details_widget: "CatalogDetailsWidget", catalog_controller: "CatalogController") -> None:
        super().__init__(catalog_details_widget)
        self.catalog_controller = catalog_controller
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.category_detail_widget = CategoryDetailWidget(self)
        self.commodities_grid_widget = CommoditiesGridWidget(self, self.catalog_controller)
        main_layout.addWidget(self.category_detail_widget, 1)
        main_layout.addWidget(self.commodities_grid_widget, 3)
        return main_layout

    def setup_ui(self, category: Category, commodities: list[Commodity]) -> None:
        self.category_detail_widget.set_category_texts(category)
        self.commodities_grid_widget.set_commodities(commodities)