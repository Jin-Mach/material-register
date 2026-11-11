from typing import TYPE_CHECKING

from PySide6.QtCore import QEvent, QObject, Qt, QTimer
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QGridLayout,
    QLineEdit,
    QVBoxLayout,
    QWidget,
)

from material_register.domain.advanced_search_dataclass import MaterialSearchDataclass
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
from material_register.utils.formatting_utils import format_number_to_locale

if TYPE_CHECKING:
    from material_register.ui.dialogs.advanced_search_dialog import AdvancedSearchDialog


class MaterialFilterDialog(QDialog):
    LESS_THAN = "<"

    EQUAL_THAN = "="

    MORE_THAN = ">"

    def __init__(
        self,
        categories: list[Category],
        commodities: list[Commodity],
        advanced_search_dialog: "AdvancedSearchDialog",
    ) -> None:
        super().__init__(advanced_search_dialog)
        self.categories = categories
        self.commodities = commodities
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
        self.material_total_price_check_box = QCheckBox()
        self.material_total_price_check_box.setObjectName("materialTotalPriceCheckBox")
        self.material_total_price_operator = QComboBox()
        self.material_total_price_operator.setObjectName("materialTotalPriceOperator")
        self.material_total_price_spinbox = QDoubleSpinBox()
        self.material_total_price_spinbox.setObjectName("materialTotalPriceSpinbox")
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.add_filter_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.add_filter_button.setObjectName("addFilterButton")
        self.add_filter_button.setDefault(True)
        self.cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setAutoDefault(False)
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
        grid_layout.addWidget(self.material_total_price_check_box, 4, 0)
        grid_layout.addWidget(self.material_total_price_operator, 4, 1)
        grid_layout.addWidget(self.material_total_price_spinbox, 4, 2)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self.setup_add_button_state()
        self._setup_comboboxes()
        self._setup_spinboxes()
        self._update_amount_suffix()
        self._update_commodity_sub_filters_state(False)
        for operator, spinbox in [
            (self.material_amount_operator, self.material_amount_spinbox),
            (
                self.material_price_per_unit_operator,
                self.material_price_per_unit_spinbox,
            ),
            (self.material_total_price_operator, self.material_total_price_spinbox),
        ]:
            MaterialFilterDialog._update_sub_filter_state(False, operator, spinbox)

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
        self.material_total_price_items = ui_texts.get(
            f"{self.material_total_price_operator.objectName()}Items", []
        )
        self.price_suffix = ui_texts.get("priceSuffix", "")
        self.category_text = ui_texts.get("categoryText", "")
        self.commodity_text = ui_texts.get("commodityText", "")
        self.material_amount_text = ui_texts.get("materialAmountText", "")
        self.price_per_unit_text = ui_texts.get("pricePerUnitText", "")
        self.total_price_text = ui_texts.get("totalPriceText", "")
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
        self.commodity_check_box.toggled.connect(
            self._update_commodity_sub_filters_state
        )
        self.material_amount_check_box.toggled.connect(
            lambda checked: MaterialFilterDialog._update_sub_filter_state(
                checked,
                self.material_amount_operator,
                self.material_amount_spinbox,
            )
        )
        self.material_price_per_unit_check_box.toggled.connect(
            lambda checked: MaterialFilterDialog._update_sub_filter_state(
                checked,
                self.material_price_per_unit_operator,
                self.material_price_per_unit_spinbox,
            )
        )
        self.material_total_price_check_box.toggled.connect(
            lambda checked: MaterialFilterDialog._update_sub_filter_state(
                checked,
                self.material_total_price_operator,
                self.material_total_price_spinbox,
            )
        )
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
        self.material_total_price_operator.addItems(self.material_total_price_items)
        for combobox in [
            self.material_amount_operator,
            self.material_price_per_unit_operator,
            self.material_total_price_operator,
        ]:
            combobox.setItemData(0, self.LESS_THAN)
            combobox.setItemData(1, self.EQUAL_THAN)
            combobox.setItemData(2, self.MORE_THAN)

    def _setup_spinboxes(self) -> None:
        spinboxes = [
            self.material_price_per_unit_spinbox,
            self.material_total_price_spinbox,
            self.material_amount_spinbox,
        ]
        self.spinboxes_line_edits = []
        for spinbox in spinboxes:
            spinbox.setMinimum(SEARCH_TRANSACTION_MIN_PRICE_VALUE)
            spinbox.setMaximum(SEARCH_TRANSACTION_MAX_PRICE_VALUE)
            spinbox.setDecimals(1)
            spinbox.setSingleStep(0.1)
            spinbox.setGroupSeparatorShown(True)
            spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)
            spinbox_line_edit = spinbox.lineEdit()
            self.spinboxes_line_edits.append(spinbox_line_edit)
            spinbox_line_edit.installEventFilter(self)
            disable_spinbox_wheel(spinbox)
        self.material_price_per_unit_spinbox.setSuffix(f" {self.price_suffix}")
        self.material_total_price_spinbox.setSuffix(f" {self.price_suffix}")

    def setup_add_button_state(self, disabled: bool = True) -> None:
        self.add_filter_button.setDisabled(disabled)

    def update_filter(self, material_filter: MaterialSearchDataclass) -> None:
        self._update_main_filters(
            material_filter.category_id, material_filter.commodity_id
        )
        if material_filter.commodity_id is not None:
            self._update_commodity_sub_filters(material_filter)
        self.setup_add_button_state(False)

    def _update_main_filters(
        self, category_id: int | None, commodity_id: int | None
    ) -> None:
        if category_id is not None:
            index = self.category_combo_box.findData(
                category_id, Qt.ItemDataRole.UserRole
            )
            if index >= 0:
                self.category_check_box.setChecked(True)
                self.category_combo_box.setCurrentIndex(index)
        if commodity_id is not None:
            index = self.commodity_combo_box.findData(
                commodity_id, Qt.ItemDataRole.UserRole
            )
            if index >= 0:
                self.commodity_check_box.setChecked(True)
                self.commodity_combo_box.setCurrentIndex(index)

    def _update_commodity_sub_filters(
        self, material_filter: MaterialSearchDataclass
    ) -> None:
        if (
            material_filter.amount_operator is not None
            and material_filter.amount_value is not None
        ):
            operator_index = self.material_amount_operator.findData(
                material_filter.amount_operator, Qt.ItemDataRole.UserRole
            )
            if operator_index >= 0:
                self.material_amount_check_box.setChecked(True)
                self.material_amount_operator.setCurrentIndex(operator_index)
                self.material_amount_spinbox.setValue(material_filter.amount_value)
        if (
            material_filter.price_per_unit_operator is not None
            and material_filter.price_per_unit_value is not None
        ):
            index = self.material_price_per_unit_operator.findData(
                material_filter.price_per_unit_operator, Qt.ItemDataRole.UserRole
            )
            if index >= 0:
                self.material_price_per_unit_check_box.setChecked(True)
                self.material_price_per_unit_operator.setCurrentIndex(index)
                self.material_price_per_unit_spinbox.setValue(
                    material_filter.price_per_unit_value
                )
        if (
            material_filter.total_price_operator is not None
            and material_filter.total_price_value is not None
        ):
            index = self.material_total_price_operator.findData(
                material_filter.total_price_operator, Qt.ItemDataRole.UserRole
            )
            if index >= 0:
                self.material_total_price_check_box.setChecked(True)
                self.material_total_price_operator.setCurrentIndex(index)
                self.material_total_price_spinbox.setValue(
                    material_filter.total_price_value
                )

    def _update_category_combobox_state(self, checked: bool) -> None:
        self.category_combo_box.setDisabled(not checked)
        self._update_add_button_state()

    def _update_commodity_combobox_state(self, checked: bool) -> None:
        self.commodity_combo_box.setDisabled(not checked)
        self._update_add_button_state()

    def _update_commodity_sub_filters_state(self, checked: bool) -> None:
        check_boxes = [
            self.material_amount_check_box,
            self.material_price_per_unit_check_box,
            self.material_total_price_check_box,
        ]
        for check_box in check_boxes:
            check_box.setEnabled(checked)
        if not checked:
            for check_box in check_boxes:
                check_box.setChecked(False)

    def _update_add_button_state(self) -> None:
        self.add_filter_button.setDisabled(True)
        for checkbox in [self.category_check_box, self.commodity_check_box]:
            if checkbox.isChecked():
                self.add_filter_button.setDisabled(False)
                return

    def _update_amount_suffix(self) -> None:
        suffix = ""
        selected_commodity_id = self.commodity_combo_box.currentData(
            Qt.ItemDataRole.UserRole
        )
        for commodity in self.commodities:
            if commodity.id == selected_commodity_id:
                suffix = str(commodity.unit)
                break
        self.material_amount_spinbox.setSuffix(f" {suffix}")

    @staticmethod
    def _update_sub_filter_state(
        checked: bool, operator: QComboBox, spinbox: QDoubleSpinBox
    ) -> None:
        operator.setEnabled(checked)
        spinbox.setEnabled(checked)
        if checked:
            spinbox.selectAll()
            spinbox.setFocus()

    def _get_main_filters(
        self, filters_text: list, material_filters: MaterialSearchDataclass
    ) -> None:
        if self.category_check_box.isChecked():
            material_filters.category_id = self.category_combo_box.currentData(
                Qt.ItemDataRole.UserRole
            )
            filters_text.append(
                f"{self.category_text} {self.category_combo_box.currentText()}"
            )
        if self.commodity_check_box.isChecked():
            material_filters.commodity_id = self.commodity_combo_box.currentData(
                Qt.ItemDataRole.UserRole
            )
            filters_text.append(
                f"{self.commodity_text} {self.commodity_combo_box.currentText()}"
            )

    def _get_commodity_sub_filters(
        self, filters_text: list, material_filters: MaterialSearchDataclass
    ) -> None:
        if self.material_amount_check_box.isChecked():
            operator = self.material_amount_operator.currentData(
                Qt.ItemDataRole.UserRole
            )
            material_filters.amount_operator = operator
            material_filters.amount_value = self.material_amount_spinbox.value()
            filters_text.append(
                f"{self.material_amount_text} {operator} "
                f"{format_number_to_locale(self.material_amount_spinbox.value())}"
                f"{self.material_amount_spinbox.suffix()}"
            )
        if self.material_price_per_unit_check_box.isChecked():
            operator = self.material_price_per_unit_operator.currentData(
                Qt.ItemDataRole.UserRole
            )
            material_filters.price_per_unit_operator = operator
            material_filters.price_per_unit_value = (
                self.material_price_per_unit_spinbox.value()
            )
            filters_text.append(
                f"{self.price_per_unit_text} {operator} "
                f"{format_number_to_locale(self.material_price_per_unit_spinbox.value())}"
                f"{self.material_price_per_unit_spinbox.suffix()}"
            )
        if self.material_total_price_check_box.isChecked():
            operator = self.material_total_price_operator.currentData(
                Qt.ItemDataRole.UserRole
            )
            material_filters.total_price_operator = operator
            material_filters.total_price_value = (
                self.material_total_price_spinbox.value()
            )
            filters_text.append(
                f"{self.total_price_text} {operator} "
                f"{format_number_to_locale(self.material_total_price_spinbox.value())}"
                f"{self.material_total_price_spinbox.suffix()}"
            )

    def get_filters_data(self) -> tuple[str, MaterialSearchDataclass]:
        filters_text = []
        material_filters = MaterialSearchDataclass()
        if self.category_check_box.isChecked() or self.commodity_check_box.isChecked():
            self._get_main_filters(filters_text, material_filters)
        if self.commodity_check_box.isChecked():
            self._get_commodity_sub_filters(filters_text, material_filters)
        return " | ".join(filters_text), material_filters

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if (
            isinstance(watched, QLineEdit)
            and watched in self.spinboxes_line_edits
            and event.type() == QEvent.Type.MouseButtonPress
        ):
            QTimer.singleShot(0, watched.selectAll)
        return super().eventFilter(watched, event)

    def showEvent(self, event: QShowEvent) -> None:
        self.adjustSize()
        self.setFixedSize(self.width() + 10, self.height() + 10)
        super().showEvent(event)
