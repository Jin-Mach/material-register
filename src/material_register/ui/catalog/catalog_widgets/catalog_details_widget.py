from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget

from material_register.domain.category_dataclass import Category
from material_register.ui.catalog.catalog_widgets.catalog_default_widget import CatalogDefaultWidget
from material_register.ui.catalog.catalog_widgets.category_with_commodities_widget import CategoryWithCommoditiesWidget
from material_register.ui.catalog.catalog_widgets.category_with_commodity_widget import CategoryWithCommodityWidget

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogDetailsWidget(QWidget):
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        super().__init__(catalog_widget)
        self.catalog_widget = catalog_widget
        self.setLayout(self._create_ui())
        self._setup_init()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.stacked_widget = QStackedWidget()
        self.catalog_default_widget = CatalogDefaultWidget(self)
        self.category_with_commodities_widget = CategoryWithCommoditiesWidget(self)
        self.category_with_commodity_widget = CategoryWithCommodityWidget(self)
        main_layout.addWidget(self.stacked_widget)
        return main_layout

    def _setup_init(self) -> None:
        widgets = [self.catalog_default_widget, self.category_with_commodities_widget,
                   self.category_with_commodity_widget]
        for widget in widgets:
            self.stacked_widget.addWidget(widget)

    def refresh_category_data(self, category_data: Category) -> None:
        self.category_with_commodities_widget.category_detail_widget.set_category_texts(category_data)
        self.category_with_commodity_widget.category_detail_widget.set_category_texts(category_data)