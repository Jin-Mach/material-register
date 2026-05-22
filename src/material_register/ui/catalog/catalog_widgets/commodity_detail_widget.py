from typing import TYPE_CHECKING

from PySide6.QtGui import QFont, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFormLayout, QCheckBox, QTextEdit

from material_register.domain.commodities_dataclass import Commodity

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.category_with_commodity_widget import CategoryWithCommodityWidget


class CommodityDetailWidget(QWidget):
    def __init__(self, category_with_commodity_widget: "CategoryWithCommodityWidget") -> None:
        super().__init__(category_with_commodity_widget)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.commodity_name_label = QLabel("Commodity Name")
        self.commodity_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.commodity_name_label.setFont(font)
        form_layout = QFormLayout()
        self.unit_label = QLabel("Unit")
        self.unit_label.setObjectName("unitLabel")
        self.unit_label_value = QLabel()
        self.default_price_label = QLabel("Default")
        self.default_price_label.setObjectName("defaultPriceLabel")
        self.default_price_label_value = QLabel()
        self.active_label = QLabel("Active")
        self.active_label.setObjectName("activeLabel")
        self.active_value = QCheckBox()
        self.notes_label = QLabel("Notes")
        self.notes_label.setObjectName("notesLabel")
        self.notes_value = QTextEdit()
        self.notes_value.setReadOnly(True)
        form_layout.addRow(self.unit_label, self.unit_label_value)
        form_layout.addRow(self.default_price_label, self.default_price_label_value)
        form_layout.addRow(self.active_label, self.active_label)
        main_layout.addWidget(self.commodity_name_label)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.notes_label)
        main_layout.addWidget(self.notes_value)
        return main_layout

    def set_commodity_text(self, commodity: Commodity) -> None:
        self.commodity_name_label.setText(commodity.name)
        self.unit_label_value.setText(commodity.unit)
        self.default_price_label_value.setText(str(commodity.default_price))
        self.active_value.setChecked(bool(commodity.active))
        self.notes_value.setPlainText(commodity.notes)