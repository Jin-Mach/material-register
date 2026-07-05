from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLabel, QPushButton, QCheckBox, \
    QSizePolicy, QHBoxLayout, QTextEdit

from material_register.domain.commodities_dataclass import Commodity
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.formating_utils import format_number_to_locale
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.commodities_grid_widget import CommoditiesGridWidget


class CommodityCardWidget(QTabWidget):
    def __init__(self,  commodities_grid_widget: "CommoditiesGridWidget") -> None:
        super().__init__(commodities_grid_widget)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.detail_widget = self._create_ui()
        self.addTab(self.detail_widget, "")

    def _create_ui(self) -> QWidget:
        detail_widget = QWidget()
        detail_layout = QVBoxLayout()
        values_layout = QFormLayout()
        self.unit_label = QLabel()
        self.unit_label.setObjectName("unitLabel")
        self.unit_value = QLabel()
        self.default_price_label = QLabel()
        self.default_price_label.setObjectName("defaultPriceLabel")
        self.default_price_value = QLabel()
        self.active_label = QLabel()
        self.active_label.setObjectName("activeLabel")
        self.active_value = QCheckBox()
        self.active_value.setDisabled(True)
        notes_layout = QFormLayout()
        self.notes_label = QLabel()
        self.notes_label.setObjectName("notesLabel")
        self.notes_value = QTextEdit()
        self.notes_value.setReadOnly(True)
        button_layout = QHBoxLayout()
        self.update_commodity_button = QPushButton()
        self.update_commodity_button.setObjectName("updateCommodityButton")
        values_layout.addRow(self.unit_label, self.unit_value)
        values_layout.addRow(self.default_price_label, self.default_price_value)
        values_layout.addRow(self.active_label, self.active_value)
        notes_layout.addRow(self.notes_label)
        notes_layout.addRow(self.notes_value)
        button_layout.addStretch()
        button_layout.addWidget(self.update_commodity_button)
        detail_layout.addLayout(values_layout)
        detail_layout.addLayout(notes_layout)
        detail_layout.addLayout(button_layout)
        detail_widget.setLayout(detail_layout)
        return detail_widget

    def setup_texts(self, ui_texts: dict[str, str]) -> None:
        widgets = [self.unit_label, self.default_price_label, self.active_label, self.notes_label,
                   self.update_commodity_button]
        if not ui_texts:
            return
        if UiTexts.set_texts(ui_texts, self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"

    def set_commodity_details(self, commodity: Commodity) -> None:
        self.setTabText(0, commodity.name)
        self.unit_value.setText(commodity.unit)
        self.default_price_value.setText(format_number_to_locale(commodity.default_price))
        self.active_value.setChecked(bool(commodity.active))
        self.notes_value.setPlainText(commodity.notes)

    def create_connection(self, commodity: Commodity, on_update_clicked) -> None:
        self.update_commodity_button.clicked.connect(lambda: on_update_clicked(commodity))

    def sizeHint(self) -> QSize:
        return QSize(250, 180)