from typing import TYPE_CHECKING

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QFont, QRegularExpressionValidator, QShowEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from material_register.config.ui_constants import (
    ADD_MODE,
    COMMODITY_DIALOG_MAX_PRICE_VALUE,
    COMMODITY_DIALOG_MIN_VALUE,
    COMMODITY_DIALOG_NOTES_LENGTH,
    UPDATE_MODE,
)
from material_register.domain.commodities_dataclass import Commodity
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.notes_length_handler import check_notes_length
from material_register.ui.helpers.styles import INVALID_INPUT_STYLE, WARNING_STYLE
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.setup.ui_widgets import disable_context_menu, setup_text_edit
from material_register.utils.normalizer import normalize_value

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


# noinspection PyTypeChecker,PyMethodMayBeStatic
class CommodityDialog(QDialog):
    def __init__(
        self,
        catalog_widget: "CatalogWidget",
        category_id: int,
        category_name: str,
        mode: str = ADD_MODE,
        commodity_data: Commodity | None = None,
    ) -> None:
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
        form_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
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
        self.warning_spacer_label = QLabel()
        self.warning_label = QLabel()
        self.warning_label.setObjectName("warningLabel")
        self.default_price_label = QLabel()
        self.default_price_label.setObjectName("defaultPriceLabel")
        self.price_input = QDoubleSpinBox()
        self.price_input.setMinimum(COMMODITY_DIALOG_MIN_VALUE)
        self.price_input.setMaximum(COMMODITY_DIALOG_MAX_PRICE_VALUE)
        self.price_input.setDecimals(1)
        self.price_input.setSingleStep(0.1)
        self.price_input.setGroupSeparatorShown(True)
        self.price_input.setValue(COMMODITY_DIALOG_MIN_VALUE)
        self.active_label = QLabel()
        self.active_label.setObjectName("activeLabel")
        self.active_checkbox = QCheckBox()
        self.active_checkbox.setObjectName("activeCheckbox")
        self.active_checkbox.setChecked(True)
        self.notes_label = QLabel()
        self.notes_label.setObjectName("notesLabel")
        self.notes_edit = QTextEdit()
        notes_count_layout = QHBoxLayout()
        self.notes_count_label = QLabel()
        self.notes_count_label.setObjectName("notesCountLabel")
        notes_count_layout.addWidget(self.notes_count_label)
        notes_count_layout.addStretch()
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Close
        )
        self.save_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.save_button.setObjectName("saveButton")
        self.close_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.close_button.setObjectName("closeButton")
        self.close_button.setDefault(True)
        form_layout.addRow(self.category_label, self.category_value)
        form_layout.addRow(self.name_label, self.name_input)
        form_layout.addRow(self.unit_label, self.unit_input)
        form_layout.addRow(self.warning_spacer_label, self.warning_label)
        form_layout.addRow(self.default_price_label, self.price_input)
        form_layout.addRow(self.active_label, self.active_checkbox)
        form_layout.addRow(self.notes_label)
        form_layout.addRow(self.notes_edit)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(notes_count_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_text_edit()
        self._setup_context_menu()
        self._setup_mode()
        self._set_validators()
        self._setup_style()
        self._update_required_styles()
        self._update_save_button_state()

    def _setup_texts(self) -> None:
        widgets = [
            self.category_label,
            self.name_label,
            self.unit_label,
            self.warning_label,
            self.default_price_label,
            self.active_label,
            self.notes_label,
            self.notes_count_label,
            self.save_button,
            self.close_button,
        ]
        texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.category_value.setText(self.category_name)
        self.units_items = texts.get(
            f"{self.unit_input.objectName()}Items", ["kg", "pcs"]
        )
        self.notes_text = texts.get(
            f"{self.notes_count_label.objectName()}Text", "Count:"
        )
        self.unit_input.addItems(self.units_items)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_text_edit(self) -> None:
        setup_text_edit(self.notes_edit)

    def _setup_context_menu(self) -> None:
        disable_context_menu(self.findChildren(QWidget))

    def _create_connection(self) -> None:
        self.name_input.textChanged.connect(self._on_form_changed)
        self.notes_edit.textChanged.connect(self._update_notes_count)
        self.save_button.clicked.connect(self.accept)
        self.close_button.clicked.connect(self.reject)

    def _setup_style(self) -> None:
        self.warning_label.setStyleSheet(WARNING_STYLE)

    def _setup_mode(self) -> None:
        if self.mode == ADD_MODE:
            self._set_add_mode()
        elif self.mode == UPDATE_MODE and self.commodity_data:
            self._set_update_mode(self.commodity_data)

    def _set_validators(self) -> None:
        commodity_validator = QRegularExpressionValidator(
            QRegularExpression(r"[\p{L}0-9 .,:&%\-\/]{1,30}")
        )
        self.name_input.setValidator(commodity_validator)

    def _set_add_mode(self) -> None:
        self.name_input.clear()
        self.unit_input.setCurrentIndex(0)
        self.notes_edit.clear()
        self.active_checkbox.setChecked(True)
        self._update_notes_count()

    def _set_update_mode(self, commodity: Commodity) -> None:
        self.name_input.setText(commodity.name or "")
        self.unit_input.setCurrentText(commodity.unit or "kg")
        self.price_input.setValue(float(commodity.default_price or 0.0))
        self.notes_edit.setPlainText(commodity.notes or "")
        self.active_checkbox.setChecked(bool(commodity.active))
        self.category_value.setText(str(self.category_name))
        self._update_notes_count()
        self.unit_input.setEnabled(False)

    def _update_notes_count(self) -> None:
        check_notes_length(
            self.notes_edit,
            self.notes_count_label,
            self.notes_text,
            COMMODITY_DIALOG_NOTES_LENGTH,
        )

    def _update_required_styles(self) -> None:
        self._set_required_style(self.name_input)

    def _set_required_style(self, widget) -> None:
        invalid = not self._is_input_valid() or not self._is_commodity_valid()
        if invalid:
            widget.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            widget.setStyleSheet("")

    def _on_form_changed(self) -> None:
        self._update_required_styles()
        self._update_save_button_state()

    def _update_save_button_state(self) -> None:
        self.save_button.setEnabled(
            self._is_input_valid() and self._is_commodity_valid()
        )

    def _is_input_valid(self) -> bool:
        name = self.name_input.text().strip()
        return bool(name)

    def _is_commodity_valid(self) -> bool:
        name = self.name_input.text().strip()
        if not name:
            return False
        ignored_id = None
        if self.mode == UPDATE_MODE and self.commodity_data:
            ignored_id = self.commodity_data.id
        return not self.catalog_widget.catalog_controller.commodity_exists(
            name, ignored_id
        )

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
            default_price=normalize_value(self.price_input.value()),
            notes=self.notes_edit.toPlainText().strip(),
            active=int(self.active_checkbox.isChecked()),
        )

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.adjustSize()
        self.setFixedSize(self.size())
        centre_dialog(self)
