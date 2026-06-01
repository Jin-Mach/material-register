from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (QWidget, QDialog, QVBoxLayout, QFormLayout, QLabel, QComboBox, QDoubleSpinBox,
                               QDialogButtonBox)

from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.transaction_items_dialog import TransactionItemsDialog


# noinspection PyTypeChecker
class CategoryCommodityDialog(QDialog):
    def __init__(self, transaction_items_dialog: "TransactionItemsDialog") -> None:
        super().__init__(transaction_items_dialog)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        self.category_label = QLabel("Category:")
        self.category_label.setObjectName("categoryLabel")
        self.category_combo_box = QComboBox()
        self.category_combo_box.addItem("Fe")
        self.commodity_label = QLabel("Commodity:")
        self.commodity_label.setObjectName("commodityLabel")
        self.commodity_combo_box = QComboBox()
        self.commodity_combo_box.addItem("Fe 12 20014005", 99)
        self.unit_label = QLabel("Unit:")
        self.unit_label.setObjectName("unitLabel")
        self.unit_label_value = QDoubleSpinBox()
        self.unit_label_value.setValue(10.0)
        self.unit_label_value.setObjectName("unitLabelValue")
        self.unit_label_value.setSuffix(" kg")
        self.price_label = QLabel("Price:")
        self.price_label.setObjectName("priceLabel")
        self.price_label_value = QDoubleSpinBox()
        self.price_label_value.setValue(5.0)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.add_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.add_button.setObjectName("addButton")
        self.cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.setObjectName("cancelButton")
        form_layout.addRow(self.category_label, self.category_combo_box)
        form_layout.addRow(self.commodity_label, self.commodity_combo_box)
        form_layout.addRow(self.unit_label, self.unit_label_value)
        form_layout.addRow(self.price_label, self.price_label_value)
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [self.category_label, self.commodity_label, self.unit_label, self.price_label, self.add_button,
                   self.cancel_button]
        self._setup_texts(widgets)

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.add_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_category_commodity_data(self) -> dict[str, str | int | float | None] | None:
        if self.commodity_combo_box.currentData() is None:
            return None
        return {
            "category": self.category_combo_box.currentText(),
            "commodity": self.commodity_combo_box.currentText(),
            "commodityId": self.commodity_combo_box.currentData(),
            "unitCount": self.unit_label_value.value(),
            "pricePerUnit": self.price_label_value.value()
        }

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        centre_dialog(self)