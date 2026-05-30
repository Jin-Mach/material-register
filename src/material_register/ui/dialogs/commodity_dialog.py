from typing import TYPE_CHECKING

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QShowEvent, QRegularExpressionValidator, QFont
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLineEdit, QLabel, QTextEdit, QHBoxLayout, QDialogButtonBox,
                               QCheckBox, QFormLayout, QDoubleSpinBox, QComboBox, QWidget)

from material_register.domain.commodities_dataclass import Commodity
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.styles import INVALID_INPUT_STYLE
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


# noinspection PyTypeChecker,PyMethodMayBeStatic
class CommodityDialog(QDialog):
    ADD_MODE = "ADD"
    UPDATE_MODE = "UPDATE"
    NOTES_LENGTH = 50

    def __init__(self, catalog_widget: "CatalogWidget", category_id: int, category_name: str, mode: str = ADD_MODE,
                 commodity_data: Commodity | None = None) -> None:
        super().__init__(catalog_widget)
        self.setMinimumWidth(400)
        self.catalog_widget = catalog_widget
        self.category_id = category_id
        self.category_name = category_name
        self.mode = mode
        self.commodity_data = commodity_data
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.category_label = QLabel()
        self.category_label.setObjectName("categoryLabel")
        self.category_value = QLabel()
        font = QFont()
        font.setBold(True)
        self.category_value.setFont(font)
        self.name_label = QLabel()
        self.name_label.setObjectName("nameLabel")
        self.name_input = QLineEdit()
        self.unit_label = QLabel()
        self.unit_label.setObjectName("unitLabel")
        self.unit_input = QComboBox()
        self.unit_input.setObjectName("unitInput")
        self.default_price_label = QLabel()
        self.default_price_label.setObjectName("defaultPriceLabel")
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(0.0)
        self.price_input.setMaximum(1000.0)
        self.price_input.setDecimals(1)
        self.price_input.setSingleStep(0.1)
        self.price_input.setValue(0.0)
        self.active_label = QLabel()
        self.active_label.setObjectName("activeLabel")
        self.active_checkbox = QCheckBox()
        self.active_checkbox.setChecked(True)
        self.notes_label = QLabel()
        self.notes_label.setObjectName("notesLabel")
        self.notes_input = QTextEdit()
        notes_count_layout = QHBoxLayout()
        self.notes_count_label = QLabel()
        self.notes_count_label.setObjectName("notesCountLabel")
        notes_count_layout.addWidget(self.notes_count_label)
        notes_count_layout.addStretch()
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Close)
        self.save_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.save_button.setObjectName("saveButton")
        self.close_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.close_button.setObjectName("closeButton")
        form_layout.addRow(self.category_label, self.category_value)
        form_layout.addRow(self.name_label, self.name_input)
        form_layout.addRow(self.unit_label, self.unit_input)
        form_layout.addRow(self.default_price_label, self.price_input)
        form_layout.addRow(self.active_label, self.active_checkbox)
        form_layout.addRow(self.notes_label)
        form_layout.addRow(self.notes_input)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(notes_count_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [
            self.category_label,
            self.name_label,
            self.unit_label,
            self.default_price_label,
            self.active_label,
            self.notes_label,
            self.notes_count_label,
            self.save_button,
            self.close_button
        ]
        self._setup_texts(widgets)
        self._setup_mode()
        self._set_validators()
        self._on_form_changed()

    def _create_connection(self) -> None:
        self.name_input.textChanged.connect(self._on_form_changed)
        self.notes_input.textChanged.connect(self._update_notes_count)
        self.save_button.clicked.connect(self.accept)
        self.close_button.clicked.connect(self.reject)

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.category_value.setText(self.category_name)
        self.units_items = texts.get(f"{self.unit_input.objectName()}Items", ["kg", "pcs"])
        self.notes_count_text = texts.get(f"{self.notes_count_label.objectName()}Text", "Count:")
        self.unit_input.addItems(self.units_items)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_mode(self) -> None:
        if self.mode == self.ADD_MODE:
            self._set_add_mode()
        elif self.mode == self.UPDATE_MODE and self.commodity_data:
            self._set_update_mode(self.commodity_data)

    def _set_validators(self) -> None:
        name_validator = QRegularExpressionValidator(QRegularExpression(r"[\p{L}0-9 .,&\-\/]{1,30}"))
        self.name_input.setValidator(name_validator)

    def _set_add_mode(self) -> None:
        self.name_input.clear()
        self.unit_input.setCurrentIndex(0)
        self.notes_input.clear()
        self.active_checkbox.setChecked(True)
        self._update_notes_count()

    def _set_update_mode(self, commodity: Commodity) -> None:
        self.name_input.setText(commodity.name or "")
        self.unit_input.setCurrentText(commodity.unit or "kg")
        self.price_input.setValue(float(commodity.default_price or 0.0))
        self.notes_input.setPlainText(commodity.notes or "")
        self.active_checkbox.setChecked(bool(commodity.active))
        self.category_value.setText(str(self.category_name))
        self._update_notes_count()

    def _update_notes_count(self) -> None:
        text = self.notes_input.toPlainText()
        if len(text) > self.NOTES_LENGTH:
            text = text[:self.NOTES_LENGTH]
            self.notes_input.blockSignals(True)
            self.notes_input.setPlainText(text)
            self.notes_input.blockSignals(False)
            cursor = self.notes_input.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.notes_input.setTextCursor(cursor)
        self.notes_count_label.setText(f"{len(text)}/{self.NOTES_LENGTH}")

    def _update_required_styles(self) -> None:
        self._set_required_style(self.name_input)

    def _set_required_style(self, widget) -> None:
        invalid = not widget.text().strip()
        if invalid:
            widget.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            widget.setStyleSheet("")

    def _on_form_changed(self) -> None:
        self._update_required_styles()
        self._update_save_button_state()

    def _update_save_button_state(self) -> None:
        self.save_button.setEnabled(self._is_input_valid() and self._is_commodity_valid())

    def _is_input_valid(self) -> bool:
        name = self.name_input.text().strip()
        if not name:
            return False
        return True

    def _is_commodity_valid(self) -> bool:
        name = self.name_input.text().strip()
        if not name:
            return False
        ignored_id = None
        if self.mode == self.UPDATE_MODE and self.commodity_data:
            ignored_id = self.commodity_data.id
        return not self.catalog_widget.catalog_controller.commodity_exists(name, ignored_id)

    def get_commodity_data(self) -> Commodity | None:
        if not self._is_input_valid():
            return None
        commodity_id = None
        if self.commodity_data:
            commodity_id = self.commodity_data.id
        return Commodity(
            id=commodity_id,
            name=self.name_input.text().strip(),
            category_id=self.category_id,
            unit=self.unit_input.currentText(),
            default_price=self.price_input.value(),
            notes=self.notes_input.toPlainText().strip(),
            active=int(self.active_checkbox.isChecked())
        )

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._update_save_button_state()
        self.adjustSize()
        self.setFixedSize(self.size())
        centre_dialog(self)