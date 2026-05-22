from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout

from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity
from material_register.ui.catalog.catalog_widgets.category_detail_widget import CategoryDetailWidget
from material_register.ui.catalog.catalog_widgets.commodity_detail_widget import CommodityDetailWidget

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.catalog_details_widget import CatalogDetailsWidget


class CategoryWithCommodityWidget(QWidget):
    def __init__(self, catalog_details_widget: "CatalogDetailsWidget") -> None:
        super().__init__(catalog_details_widget)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.category_detail_widget = CategoryDetailWidget(self)
        self.commodity_detail_widget = CommodityDetailWidget(self)
        main_layout.addWidget(self.category_detail_widget)
        return main_layout

    def setup_ui(self, category: Category, commodity: Commodity) -> None:
        self.category_detail_widget.set_category_texts(category)
        self.commodity_detail_widget.set_commodity_text(commodity)
