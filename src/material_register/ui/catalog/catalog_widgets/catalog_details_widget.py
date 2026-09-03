from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGroupBox, QStackedWidget, QVBoxLayout, QWidget

from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity
from material_register.ui.catalog.catalog_widgets.catalog_default_widget import (
    CatalogDefaultWidget,
)
from material_register.ui.catalog.catalog_widgets.category_with_commodities_widget import (
    CategoryWithCommoditiesWidget,
)

if TYPE_CHECKING:
    from material_register.controllers.catalog_controller import CatalogController
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogDetailsWidget(QWidget):
    def __init__(
        self, catalog_widget: "CatalogWidget", catalog_controller: "CatalogController"
    ) -> None:
        super().__init__(catalog_widget)
        self.catalog_widget = catalog_widget
        self.catalog_controller = catalog_controller
        self.setLayout(self._create_ui())
        self._setup_init()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        group_box = QGroupBox()
        group_layout = QVBoxLayout()
        group_layout.setContentsMargins(0, 0, 0, 0)
        group_layout.setSpacing(5)
        self.stacked_widget = QStackedWidget()
        self.catalog_default_widget = CatalogDefaultWidget(self)
        self.category_with_commodities_widget = CategoryWithCommoditiesWidget(
            self, self.catalog_controller
        )
        group_layout.addWidget(self.stacked_widget)
        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)
        return main_layout

    def _setup_init(self) -> None:
        widgets = [self.catalog_default_widget, self.category_with_commodities_widget]
        for widget in widgets:
            self.stacked_widget.addWidget(widget)

    def refresh_category_data(self, category_data: Category) -> None:
        self.category_with_commodities_widget.category_detail_widget.set_category_texts(
            category_data
        )

    def show_default_details(self) -> None:
        self.stacked_widget.setCurrentIndex(0)

    def show_category_details(
        self, category: Category, commodities: list[Commodity]
    ) -> None:
        self.stacked_widget.setCurrentIndex(1)
        self.category_with_commodities_widget.setup_ui(category, commodities)
