from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from material_register.config.ui_constants import (
    COMMODITY_DIALOG_MAX_PRICE_VALUE,
    COMMODITY_DIALOG_MIN_VALUE,
)
from material_register.domain.commodities_dataclass import Commodity
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class UpdateCommoditiesPriceDialog(QDialog):
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        super().__init__(catalog_widget)
        self.commodities_map = {}
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        self.commodities_widget = QWidget()
        self.commodities_layout = QGridLayout()
        self.commodities_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.commodities_widget.setLayout(self.commodities_layout)
        self.commodity_name_label = QLabel()
        self.commodity_name_label.setObjectName("commodityNameLabel")
        self.default_price_label = QLabel()
        self.default_price_label.setObjectName("defaultPriceLabel")
        self.new_price_label = QLabel()
        self.new_price_label.setObjectName("newPriceLabel")
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setSizeAdjustPolicy(
            QScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scroll_area.setWidget(self.commodities_widget)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.save_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.save_button.setObjectName("saveButton")
        self.save_button.setDisabled(True)
        self.cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setDefault(True)
        self.commodities_layout.addWidget(self.commodity_name_label, 0, 0)
        self.commodities_layout.addWidget(self.default_price_label, 0, 1)
        self.commodities_layout.addWidget(self.new_price_label, 0, 2)
        main_layout.addWidget(self.scroll_area)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_labels()

    def _setup_texts(self) -> None:
        if UiTexts.set_ui_texts(self, self.findChildren(QWidget)):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_labels(self) -> None:
        for label in [
            self.commodity_name_label,
            self.default_price_label,
            self.new_price_label,
        ]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def _create_connection(self) -> None:
        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def setup_commodities(self, commodities: list[Commodity]) -> None:
        for index, commodity in enumerate(commodities):
            row = index + 1
            name_label = QLabel(commodity.name)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = QFont()
            font.setBold(True)
            name_label.setFont(font)
            price_label = QLabel(str(commodity.default_price))
            price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_spinbox = QDoubleSpinBox()
            value_spinbox.setValue(commodity.default_price)
            value_spinbox.setProperty("default_price", commodity.default_price)
            value_spinbox.setSuffix(commodity.unit)
            value_spinbox.setMinimum(COMMODITY_DIALOG_MIN_VALUE)
            value_spinbox.setMaximum(COMMODITY_DIALOG_MAX_PRICE_VALUE)
            value_spinbox.setDecimals(1)
            value_spinbox.setGroupSeparatorShown(True)
            value_spinbox.valueChanged.connect(self._update_button_state)
            self.commodities_layout.addWidget(name_label, row, 0)
            self.commodities_layout.addWidget(price_label, row, 1)
            self.commodities_layout.addWidget(value_spinbox, row, 2)
            self.commodities_map[commodity.id] = value_spinbox
        self._setup_dialog_size()

    def _setup_dialog_size(self) -> None:
        self.commodities_widget.adjustSize()
        width = self.commodities_widget.sizeHint().width()
        self.scroll_area.setMinimumWidth(width)
        self.adjustSize()
        self.setFixedWidth(self.width() + 10)
        self.setFixedHeight(500)

    def _update_button_state(self) -> None:
        for spinbox in self.commodities_map.values():
            if spinbox.value() != spinbox.property("default_price"):
                self.save_button.setDisabled(False)
                return
        self.save_button.setDisabled(True)
