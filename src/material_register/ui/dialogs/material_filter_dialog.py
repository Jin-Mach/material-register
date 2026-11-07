from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QVBoxLayout,
    QWidget,
)

from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    SEARCH_TRANSACTION_MAX_PRICE_VALUE,
    SEARCH_TRANSACTION_MIN_PRICE_VALUE,
    UI_MARGINS_5,
    UI_MARGINS_10,
    UI_SPACING,
)
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.setup.ui_widgets import disable_spinbox_wheel

if TYPE_CHECKING:
    from material_register.ui.dialogs.advanced_search_dialog import AdvancedSearchDialog


class MaterialFilterDialog(QDialog):
    def __init__(
        self,
        categories: list[Category],
        commodities: list[Commodity],
        advanced_search_dialog: "AdvancedSearchDialog",
        update: bool = False,
    ) -> None:
        super().__init__(advanced_search_dialog)
        self.categories = categories
        self.commodities = commodities
        self.update = update
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_10)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(UI_SPACING * 4)
        grid_layout.setVerticalSpacing(UI_SPACING)
        grid_layout.setContentsMargins(*UI_MARGINS_5)
        grid_layout.setContentsMargins(*UI_MARGINS_5)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 2)
        grid_layout.setColumnStretch(2, 2)
        self.category_check_box = QCheckBox()
        self.category_check_box.setObjectName("categoryCheckBox")
        self.category_combo_box = QComboBox()
        self.category_combo_box.setObjectName("categoryComboBox")
        self.commodity_check_box = QCheckBox()
        self.commodity_check_box.setObjectName("commodityCheckBox")
        self.commodity_combo_box = QComboBox()
        self.commodity_combo_box.setObjectName("commodityComboBox")
        self.material_amount_check_box = QCheckBox()
        self.material_amount_check_box.setObjectName("materialAmountCheckBox")
        self.material_amount_operator = QComboBox()
        self.material_amount_operator.setObjectName("materialAmountOperator")
        self.material_amount_spinbox = QDoubleSpinBox()
        self.material_amount_spinbox.setObjectName("materialAmountSpinBox")
        self.material_price_per_unit_check_box = QCheckBox()
        self.material_price_per_unit_check_box.setObjectName(
            "materialPricePerUnitCheckBox"
        )
        self.material_price_per_unit_operator = QComboBox()
        self.material_price_per_unit_operator.setObjectName(
            "materialPricePerUnitOperator"
        )
        self.material_price_per_unit_spinbox = QDoubleSpinBox()
        self.material_price_per_unit_spinbox.setObjectName(
            "materialPricePerUnitSpinbox"
        )
        self.material_total_price_per_unit_check_box = QCheckBox()
        self.material_total_price_per_unit_check_box.setObjectName(
            "materialTotalPricePerUnitCheckBox"
        )
        self.material_total_price_per_unit_operator = QComboBox()
        self.material_total_price_per_unit_operator.setObjectName(
            "materialTotalPricePerUnitOperator"
        )
        self.material_total_price_per_unit_spinbox = QDoubleSpinBox()
        self.material_total_price_per_unit_spinbox.setObjectName(
            "materialTotalPricePerUnitSpinbox"
        )
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.add_filter_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.add_filter_button.setObjectName("addFilterButton")
        self.cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.setObjectName("cancelButton")
        grid_layout.addWidget(self.category_check_box, 0, 0)
        grid_layout.addWidget(self.category_combo_box, 0, 1)
        grid_layout.addWidget(self.commodity_check_box, 1, 0)
        grid_layout.addWidget(self.commodity_combo_box, 1, 1)
        grid_layout.addWidget(self.material_amount_check_box, 2, 0)
        grid_layout.addWidget(self.material_amount_operator, 2, 1)
        grid_layout.addWidget(self.material_amount_spinbox, 2, 2)
        grid_layout.addWidget(self.material_price_per_unit_check_box, 3, 0)
        grid_layout.addWidget(self.material_price_per_unit_operator, 3, 1)
        grid_layout.addWidget(self.material_price_per_unit_spinbox, 3, 2)
        grid_layout.addWidget(self.material_total_price_per_unit_check_box, 4, 0)
        grid_layout.addWidget(self.material_total_price_per_unit_operator, 4, 1)
        grid_layout.addWidget(self.material_total_price_per_unit_spinbox, 4, 2)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_comboboxes()
        self._setup_spinboxes()
        self._update_amount_suffix()
        self._update_commodity_sub_filters_state(False)

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            ErrorHandler.handle_error(
                f"Texts load failed: {self.__class__.__name__}",
                LOGGER_UI,
                LOG_LEVEL_WARNING,
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.material_amount_items = ui_texts.get(
            f"{self.material_amount_operator.objectName()}Items", []
        )
        self.material_price_per_unit_items = ui_texts.get(
            f"{self.material_price_per_unit_operator.objectName()}Items", []
        )
        self.material_total_price_per_unit_items = ui_texts.get(
            f"{self.material_total_price_per_unit_operator.objectName()}Items", []
        )
        self.price_suffix = ui_texts.get("priceSuffix", "")
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.category_check_box.toggled.connect(self._update_category_combobox_state)
        self.commodity_check_box.toggled.connect(self._update_commodity_combobox_state)
        self.commodity_combo_box.currentIndexChanged.connect(self._update_amount_suffix)
        self.commodity_check_box.toggled.connect(self._update_commodity_sub_filters_state)
        self.add_filter_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def _setup_comboboxes(self) -> None:
        for category in self.categories:
            self.category_combo_box.addItem(category.name, category.id)
        self.category_combo_box.setDisabled(True)
        for commodity in self.commodities:
            self.commodity_combo_box.addItem(commodity.name, commodity.id)
        self.commodity_combo_box.setDisabled(True)
        self.material_amount_operator.addItems(self.material_amount_items)
        self.material_price_per_unit_operator.addItems(
            self.material_price_per_unit_items
        )
        self.material_total_price_per_unit_operator.addItems(
            self.material_total_price_per_unit_items
        )

    def _setup_spinboxes(self) -> None:
        spinboxes = [
            self.material_price_per_unit_spinbox,
            self.material_total_price_per_unit_spinbox,
            self.material_amount_spinbox,
        ]
        for spinbox in spinboxes:
            spinbox.setMinimum(SEARCH_TRANSACTION_MIN_PRICE_VALUE)
            spinbox.setMaximum(SEARCH_TRANSACTION_MAX_PRICE_VALUE)
            spinbox.setDecimals(1)
            spinbox.setSingleStep(0.1)
            spinbox.setGroupSeparatorShown(True)
            spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)
            disable_spinbox_wheel(spinbox)
        self.material_price_per_unit_spinbox.setSuffix(f" {self.price_suffix}")
        self.material_total_price_per_unit_spinbox.setSuffix(f" {self.price_suffix}")

    def _update_category_combobox_state(self, checked: bool) -> None:
        self.category_combo_box.setDisabled(not checked)

    def _update_commodity_combobox_state(self, checked: bool) -> None:
        self.commodity_combo_box.setDisabled(not checked)

    def _update_commodity_sub_filters_state(self, checked: bool) -> None:
        check_boxes = [self.material_amount_check_box, self.material_price_per_unit_check_box, self.material_total_price_per_unit_check_box]
        operators = [self.material_amount_operator, self.material_price_per_unit_operator, self.material_total_price_per_unit_operator]
        spinboxes = [self.material_amount_spinbox, self.material_price_per_unit_spinbox, self.material_total_price_per_unit_spinbox]
        widgets = check_boxes + operators + spinboxes
        for widget in widgets:
            widget.setDisabled(not checked)
        if not checked:
            for check_box in check_boxes:
                check_box.setChecked(checked)

    def _update_amount_suffix(self) -> None:
        suffix = ""
        selected_commodity_id = self.commodity_combo_box.currentData(Qt.ItemDataRole.UserRole)
        for commodity in self.commodities:
            if commodity.id == selected_commodity_id:
                suffix = str(commodity.unit)
                break
        self.material_amount_spinbox.setSuffix(f" {suffix}")

    def showEvent(self, event: QShowEvent) -> None:
        self.adjustSize()
        self.setFixedSize(self.width() + 10, self.height() + 10)
        super().showEvent(event)
