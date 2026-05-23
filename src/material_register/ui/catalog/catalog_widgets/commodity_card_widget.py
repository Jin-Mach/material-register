from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLabel

from material_register.domain.commodities_dataclass import Commodity

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.commodities_grid_widget import CommoditiesGridWidget


class CommodityCardWidget(QTabWidget):
    def __init__(self,  commodities_grid_widget: "CommoditiesGridWidget") -> None:
        super().__init__(commodities_grid_widget)

    def _create_ui(self) -> QWidget:
        detail_widget = QWidget()
        detail_layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.unit_label = QLabel("Unit:")
        self.unit_label.setObjectName("unitLabel")
        self.unit_value = QLabel()
        self.default_price_label = QLabel("Default:")
        self.default_price_label.setObjectName("defaultPriceLabel")
        self.default_price_value = QLabel()
        form_layout.addRow(self.unit_label, self.unit_value)
        form_layout.addRow(self.default_price_label, self.default_price_value)
        detail_layout.addLayout(form_layout)
        detail_widget.setLayout(detail_layout)
        return detail_widget

    def set_commodity_details(self, commodity: Commodity) -> None:
        self.addTab(self._create_ui(), commodity.name)
        self.unit_value.setText(str(commodity.unit))
        self.default_price_value.setText(str(commodity.default_price))