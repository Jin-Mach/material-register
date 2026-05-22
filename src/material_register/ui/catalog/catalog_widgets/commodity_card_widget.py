from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout

from material_register.domain.commodities_dataclass import Commodity

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.commodities_grid_widget import CommoditiesGridWidget


class CommodityCardWidget(QTabWidget):
    def __init__(self,  commodities_grid_widget: "CommoditiesGridWidget") -> None:
        super().__init__(commodities_grid_widget)

    def _create_ui(self) -> QWidget:
        detail_widget = QWidget()
        detail_layout = QVBoxLayout()
        detail_widget.setLayout(detail_layout)
        return detail_widget

    def set_commodity_details(self, commodity: Commodity) -> None:
        self.addTab(self._create_ui(), commodity.name)