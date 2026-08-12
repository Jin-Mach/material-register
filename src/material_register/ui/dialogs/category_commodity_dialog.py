from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFontMetrics, QShowEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from material_register.config.ui_constants import (
    CATEGORY_COMMODITY_DIALOG_MAX_PRICE_VALUE,
    CATEGORY_COMMODITY_DIALOG_MAX_UNIT_VALUE,
    CATEGORY_COMMODITY_DIALOG_MIN_VALUE,
    INTEGER_SUFFIXES,
    TRANSFER_OUT,
)
from material_register.domain.category_dataclass import Category
from material_register.domain.commodities_dataclass import Commodity
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.helpers.spinbox_setup import set_suffix_mode
from material_register.ui.helpers.styles import INVALID_INPUT_STYLE
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_texts import UiTexts
from material_register.utils.normalizer import normalize_value

if TYPE_CHECKING:
    from material_register.ui.dialogs.transaction_items_dialog_in import (
        TransactionItemsDialogIn,
    )


# noinspection PyTypeChecker,SpellCheckingInspection
class CategoryCommodityDialog(QDialog):
    def __init__(
        self,
        categories: list[Category],
        commodities: list[Commodity],
        transaction_items_dialog: "TransactionItemsDialogIn",
        transfer_type: str,
    ) -> None:
        super().__init__(transaction_items_dialog)
        self.categories = categories
        self.commodities = commodities
        self.transfer_type = transfer_type
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.category_label = QLabel()
        self.category_label.setObjectName("categoryLabel")
        self.category_combo_box = QComboBox()
        self.category_combo_box.setObjectName("categoryComboBox")
        self.commodity_label = QLabel()
        self.commodity_label.setObjectName("commodityLabel")
        self.commodity_combo_box = QComboBox()
        self.commodity_combo_box.setObjectName("commodityComboBox")
        self.unit_label = QLabel()
        self.unit_label.setObjectName("unitLabel")
        self.unit_spinbox = QDoubleSpinBox()
        self.price_label = QLabel("Price:")
        self.price_label.setObjectName("priceLabel")
        self.price_spinbox = QDoubleSpinBox()
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.add_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.add_button.setObjectName("addButton")
        self.cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.setObjectName("cancelButton")
        form_layout.addRow(self.category_label, self.category_combo_box)
        form_layout.addRow(self.commodity_label, self.commodity_combo_box)
        form_layout.addRow(self.unit_label, self.unit_spinbox)
        form_layout.addRow(self.price_label, self.price_spinbox)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_widgets()
        self._setup_spinboxes()
        self._setup_texts()
        self._setup_categories_items()
        self._on_value_changed()

    def _setup_texts(self) -> None:
        widgets = [
            self.category_label,
            self.category_combo_box,
            self.commodity_label,
            self.commodity_combo_box,
            self.unit_label,
            self.price_label,
            self.add_button,
            self.cancel_button,
        ]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.category_combo_box.currentIndexChanged.connect(
            self._setup_commodities_items
        )
        self.category_combo_box.currentIndexChanged.connect(self._on_value_changed)
        self.commodity_combo_box.currentIndexChanged.connect(
            self._setup_commodity_values
        )
        self.commodity_combo_box.currentIndexChanged.connect(self._on_value_changed)
        self.unit_spinbox.valueChanged.connect(self._on_value_changed)
        self.price_spinbox.valueChanged.connect(self._on_value_changed)
        self.add_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def _setup_widgets(self) -> None:
        for widget in (
            self.commodity_combo_box,
            self.unit_spinbox,
            self.price_spinbox,
            self.add_button,
        ):
            widget.setEnabled(False)
        if self.transfer_type == TRANSFER_OUT:
            self.price_label.hide()
            self.price_spinbox.hide()

    def _setup_spinboxes(self) -> None:
        self._setup_unit_spinbox()
        self._setup_price_spinbox()

    def _setup_unit_spinbox(self) -> None:
        self.unit_spinbox.setMinimum(CATEGORY_COMMODITY_DIALOG_MIN_VALUE)
        self.unit_spinbox.setMaximum(CATEGORY_COMMODITY_DIALOG_MAX_UNIT_VALUE)
        self.unit_spinbox.setDecimals(1)
        self.unit_spinbox.setSingleStep(0.1)
        self.unit_spinbox.setGroupSeparatorShown(True)

    def _setup_price_spinbox(self) -> None:
        self.price_spinbox.setMinimum(CATEGORY_COMMODITY_DIALOG_MIN_VALUE)
        self.price_spinbox.setMaximum(CATEGORY_COMMODITY_DIALOG_MAX_PRICE_VALUE)
        self.price_spinbox.setDecimals(1)
        self.price_spinbox.setSingleStep(0.1)
        self.price_spinbox.setGroupSeparatorShown(True)

    def _setup_categories_items(self) -> None:
        self.category_combo_box.clear()
        for index, category in enumerate(self.categories):
            if self._has_commodity(category):
                self.category_combo_box.addItem(category.name, category.id)
        self.category_combo_box.setCurrentIndex(-1)
        QTimer.singleShot(
            0,
            lambda: CategoryCommodityDialog._adjust_combo_view_width(
                self.category_combo_box
            ),
        )

    def _setup_commodities_items(self) -> None:
        self.commodity_combo_box.clear()
        category_id = self.category_combo_box.currentData()
        if category_id is None:
            return
        index = 0
        for commodity in self.commodities:
            if commodity.category_id == category_id:
                self.commodity_combo_box.addItem(commodity.name, commodity.id)
                index += 1
        self.commodity_combo_box.setCurrentIndex(-1)
        self._reset_spinboxes_values()
        CategoryCommodityDialog._setup_enable_state(
            enabled=[self.commodity_combo_box],
            disabled=[self.unit_spinbox, self.price_spinbox, self.add_button],
        )
        QTimer.singleShot(
            0, lambda: self._adjust_combo_view_width(self.commodity_combo_box)
        )

    def _setup_commodity_values(self) -> None:
        commodity_id = self.commodity_combo_box.currentData()
        if commodity_id is None:
            return
        for commodity in self.commodities:
            if commodity.id == commodity_id:
                self.commodity_suffix = commodity.unit
                self.unit_spinbox.setValue(CATEGORY_COMMODITY_DIALOG_MIN_VALUE)
                self.unit_spinbox.setSuffix(f"  {self.commodity_suffix}")
                set_suffix_mode(self.unit_spinbox, self.commodity_suffix)
                self.price_spinbox.setValue(commodity.default_price)
                break
        CategoryCommodityDialog._setup_enable_state(
            enabled=[self.unit_spinbox, self.price_spinbox]
        )

    def setup_update(self, item_data) -> None:
        self._setup_categories_items()
        self.category_combo_box.setCurrentText(item_data["category"])
        self._setup_commodities_items()
        self.commodity_combo_box.setCurrentText(item_data["commodity"])
        self.unit_spinbox.setValue(item_data["unitCount"])
        self.price_spinbox.setValue(item_data["pricePerUnit"])

    def _reset_spinboxes_values(self) -> None:
        self.unit_spinbox.setValue(CATEGORY_COMMODITY_DIALOG_MIN_VALUE)
        self.unit_spinbox.setSuffix("")
        self.price_spinbox.setValue(CATEGORY_COMMODITY_DIALOG_MIN_VALUE)

    def _on_value_changed(self) -> None:
        self._set_required_style()
        self._update_button_state()

    def _has_commodity(self, category: Category) -> bool:
        for commodity in self.commodities:
            if commodity.category_id == category.id:
                return True
        return False

    def _update_button_state(self) -> None:
        valid = self._is_valid()
        self.add_button.setEnabled(valid)

    def _set_required_style(self) -> None:
        if CategoryCommodityDialog._is_unit_valid_value(self.unit_spinbox.value()):
            self.unit_spinbox.setStyleSheet("")
        else:
            self.unit_spinbox.setStyleSheet(INVALID_INPUT_STYLE)
        if self.transfer_type != TRANSFER_OUT:
            if CategoryCommodityDialog._is_price_valid_value(
                self.price_spinbox.value()
            ):
                self.price_spinbox.setStyleSheet("")
            else:
                self.price_spinbox.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            self.price_spinbox.setStyleSheet("")

    def _normalize_unit_price_values(self) -> tuple[int | float, int | float]:
        unit = normalize_value(self.unit_spinbox.value())
        price = normalize_value(self.price_spinbox.value())
        if self.commodity_suffix in INTEGER_SUFFIXES:
            unit = int(unit)
        if self.transfer_type == TRANSFER_OUT:
            return unit, 0
        return unit, price

    def _is_valid(self) -> bool:
        if self.transfer_type == TRANSFER_OUT:
            return (
                self.category_combo_box.currentIndex() != -1
                and self.commodity_combo_box.currentIndex() != -1
                and CategoryCommodityDialog._is_unit_valid_value(
                    self.unit_spinbox.value()
                )
            )
        return (
            self.category_combo_box.currentIndex() != -1
            and self.commodity_combo_box.currentIndex() != -1
            and CategoryCommodityDialog._is_unit_valid_value(self.unit_spinbox.value())
            and CategoryCommodityDialog._is_price_valid_value(
                self.price_spinbox.value()
            )
        )

    @staticmethod
    def _adjust_combo_view_width(combobox: QComboBox) -> None:
        font_metrics = QFontMetrics(combobox.font())
        max_width = 0
        for i in range(combobox.count()):
            text = combobox.itemText(i)
            max_width = max(max_width, font_metrics.horizontalAdvance(text))
        combobox.view().setMinimumWidth(max_width + 40)

    @staticmethod
    def _setup_enable_state(
        enabled: list[QWidget] | None = None, disabled: list[QWidget] | None = None
    ) -> None:
        if enabled is not None:
            for widget in enabled:
                widget.setEnabled(True)
        if disabled is not None:
            for widget in disabled:
                widget.setEnabled(False)

    @staticmethod
    def _is_unit_valid_value(value: float) -> bool:
        return normalize_value(value) > CATEGORY_COMMODITY_DIALOG_MIN_VALUE

    @staticmethod
    def _is_price_valid_value(value: float) -> bool:
        return normalize_value(value) >= CATEGORY_COMMODITY_DIALOG_MIN_VALUE

    def _valid_values(self) -> bool:
        if self.transfer_type == TRANSFER_OUT:
            return CategoryCommodityDialog._is_unit_valid_value(
                self.unit_spinbox.value()
            )
        return CategoryCommodityDialog._is_unit_valid_value(
            self.unit_spinbox.value()
        ) and CategoryCommodityDialog._is_price_valid_value(self.price_spinbox.value())

    def get_category_commodity_data(self) -> dict[str, str | int | float | None] | None:
        commodity_id = self.commodity_combo_box.currentData()
        if commodity_id is None or not self._valid_values():
            return None
        if (
            self.transfer_type != TRANSFER_OUT
            and self.price_spinbox.value() == CATEGORY_COMMODITY_DIALOG_MIN_VALUE
        ):
            question = MessageBoxes.show_question(
                self,
                "ZERO_PRICE_TRANSACTION",
                f"{self.category_combo_box.currentText()} {self.commodity_combo_box.currentText()}",
            )
            if not question:
                return None
        unit_count, price_per_unit = self._normalize_unit_price_values()
        return {
            "category": self.category_combo_box.currentText(),
            "commodity": self.commodity_combo_box.currentText(),
            "commoditySuffix": self.commodity_suffix,
            "commodityId": commodity_id,
            "unitCount": unit_count,
            "pricePerUnit": price_per_unit,
        }

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.adjustSize()
        self.setFixedSize(self.size())
        centre_dialog(self)
