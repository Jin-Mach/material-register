from datetime import datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QRegularExpressionValidator, QShowEvent
from PySide6.QtWidgets import QDialog, QVBoxLayout, QComboBox, QFormLayout, QLabel, QLineEdit, QTextEdit, QHBoxLayout, \
    QDialogButtonBox, QCheckBox

from material_register.domain.customers_dataclass import Customer
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.customers.customers_widget import CustomersWidget

# noinspection PyTypeChecker,PyMethodMayBeStatic
class CustomerDialog(QDialog):
    ADD_MODE = "ADD"
    UPDATE_MODE = "UPDATE"
    NOTES_LENGTH = 200
    INDIVIDUAL_INDEX = 0
    COMPANY_INDEX = 1

    def __init__(self, customers_widget: "CustomersWidget", mode: str = ADD_MODE, customer_data: "Customer" = None) -> None:
        super().__init__(customers_widget)
        self.setMinimumWidth(400)
        self.mode = mode
        self.customer_data = customer_data
        self.customers_widget = customers_widget
        self.mode = mode
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.created_label = QLabel()
        self.created_label.setObjectName("createdLabel")
        self.created_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subject_layout = QHBoxLayout()
        self.subject_type = QComboBox()
        self.subject_type.setObjectName("subjectType")
        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.company_label = QLabel()
        self.company_label.setObjectName("companyLabel")
        self.company_input = QLineEdit()
        self.first_name_label = QLabel()
        self.first_name_label.setObjectName("firstNameLabel")
        self.first_name_input = QLineEdit()
        self.last_name_label = QLabel()
        self.last_name_label.setObjectName("lastNameLabel")
        self.last_name_input = QLineEdit()
        self.document_type_label = QLabel()
        self.document_type_label.setObjectName("documentTypeLabel")
        self.document_type_input = QLineEdit()
        self.address_label = QLabel()
        self.address_label.setObjectName("addressLabel")
        self.active_label = QLabel()
        self.active_label.setObjectName("activeLabel")
        self.active_checkbox = QCheckBox()
        self.active_checkbox.setChecked(True)
        self.address_input = QLineEdit()
        self.notes_label = QLabel()
        self.notes_label.setObjectName("notesLabel")
        self.notes_input = QTextEdit()
        notes_count_layout = QHBoxLayout()
        self.notes_count_label = QLabel()
        self.notes_count_label.setObjectName("notesCountLabel")
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Close)
        self.save_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.save_button.setObjectName("saveButton")
        self.close_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.close_button.setObjectName("closeButton")
        subject_layout.addStretch()
        subject_layout.addWidget(self.subject_type)
        subject_layout.addStretch()
        form_layout.addRow(self.company_label, self.company_input)
        form_layout.addRow(self.first_name_label, self.first_name_input)
        form_layout.addRow(self.last_name_label, self.last_name_input)
        form_layout.addRow(self.document_type_label, self.document_type_input)
        form_layout.addRow(self.address_label, self.address_input)
        form_layout.addRow(self.active_label, self.active_checkbox)
        form_layout.addRow(self.notes_label)
        form_layout.addRow(self.notes_input)
        notes_count_layout.addWidget(self.notes_count_label)
        notes_count_layout.addStretch()
        main_layout.addWidget(self.created_label)
        main_layout.addLayout(subject_layout)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(notes_count_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [self.subject_type, self.company_label, self.first_name_label, self.last_name_label,
                   self.document_type_label, self.address_label, self.active_label, self.notes_label,
                   self.notes_count_label, self.save_button, self.close_button]
        self._setup_texts(widgets)
        self._setup_items()
        self._setup_mode()
        self._set_validators()

    def _create_connection(self) -> None:
        for widget in (self.first_name_input, self.last_name_input, self.company_input, self.document_type_input,
                       self.address_input):
            widget.textChanged.connect(self._on_form_changed)
        self.subject_type.currentIndexChanged.connect(self._on_type_changed)
        self.document_type_input.textChanged.connect(self._on_document_type_changed)
        self.notes_input.textChanged.connect(self._update_notes_count)
        self.save_button.clicked.connect(self.accept)
        self.close_button.clicked.connect(self.reject)

    def _setup_texts(self, widgets: list) -> None:
        texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.created_label_text = texts.get(f"{self.created_label.objectName()}Text", "Created:")
        self.notes_count_text = texts.get(f"{self.notes_count_label.objectName()}Text", "Count:")
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_items(self) -> None:
        self.subject_type.clear()
        texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        items = texts.get(f"{self.subject_type.objectName()}Items", ["Individual", "Company"])
        if not items:
            ErrorHandler.handle_error(f"Items texts load failed: {self.__class__.__name__}", "ui", "warning")
            return
        for index, text in enumerate(items):
            self.subject_type.addItem(text, index)

    def _setup_mode(self) -> None:
        if self.mode == self.ADD_MODE:
            self._set_add_mode()
        elif self.mode == self.UPDATE_MODE and self.customer_data:
            self._set_update_mode(self.customer_data)

    def _set_validators(self) -> None:
        name_validator = QRegularExpressionValidator(QRegularExpression(r"[\p{L}]{1,30}"))
        company_validator = QRegularExpressionValidator(QRegularExpression(r"[\p{L}0-9 .,&\-]{1,50}"))
        document_validator = QRegularExpressionValidator(QRegularExpression(r"[0-9A-Za-z \-/]{1,30}"))
        address_validator = QRegularExpressionValidator(QRegularExpression(r"[\p{L}0-9 .,\-/]{1,50}"))
        self.first_name_input.setValidator(name_validator)
        self.last_name_input.setValidator(name_validator)
        self.company_input.setValidator(company_validator)
        self.document_type_input.setValidator(document_validator)
        self.address_input.setValidator(address_validator)

    def _apply_type_state(self) -> None:
        index = self.subject_type.currentIndex()
        if index == 0:
            self.first_name_input.setEnabled(True)
            self.last_name_input.setEnabled(True)
            self.company_input.setEnabled(False)
            self.first_name_input.setFocus()
        elif index == 1:
            self.first_name_input.setEnabled(False)
            self.last_name_input.setEnabled(False)
            self.company_input.setEnabled(True)
            self.company_input.setFocus()
        else:
            self.first_name_input.setEnabled(False)
            self.last_name_input.setEnabled(False)
            self.company_input.setEnabled(False)
            self.save_button.setEnabled(False)
        enabled = index in (0, 1)
        self.document_type_input.setEnabled(enabled)
        self.address_input.setEnabled(enabled)
        self.active_checkbox.setEnabled(enabled)
        self.notes_input.setEnabled(enabled)

    def _update_notes_count(self):
        text = self.notes_input.toPlainText()
        if len(text) > self.NOTES_LENGTH:
            text = text[:self.NOTES_LENGTH]
            self.notes_input.blockSignals(True)
            self.notes_input.setPlainText(text)
            self.notes_input.blockSignals(False)
            cursor = self.notes_input.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.notes_input.setTextCursor(cursor)
        self.notes_count_label.setText(
            f"{self.notes_count_text} {len(text)}/{self.NOTES_LENGTH}"
        )

    def _update_required_styles(self) -> None:
        for widget in (self.first_name_input, self.last_name_input, self.company_input, self.address_input):
            self._set_required_style(widget)

    def _set_required_style(self, widget) -> None:
        if widget.isEnabled() and not widget.text().strip():
            widget.setStyleSheet("QLineEdit { background: #ffdddd; border: 1px solid red; }")
        else:
            widget.setStyleSheet("")

    def _on_document_type_changed(self) -> None:
        if self._is_document_valid():
            self.document_type_input.setStyleSheet("")
        else:
            self.document_type_input.setStyleSheet("QLineEdit { background: #ffdddd; border: 1px solid red; }")

    def _update_save_button_state(self) -> None:
        type_index = self.subject_type.currentIndex()
        self.save_button.setEnabled(self._is_input_valid(type_index) and self._is_document_valid())

    def _on_form_changed(self) -> None:
        self._update_required_styles()
        self._on_document_type_changed()
        self._update_save_button_state()

    def _on_type_changed(self):
        self._apply_type_state()
        self._on_form_changed()

    def get_customer_data(self) -> Customer | None:
        type_index = self.subject_type.currentIndex()
        if not self._is_input_valid(type_index):
            return None
        if type_index == 0:
            return Customer(
                company=None,
                first_name=self.first_name_input.text().strip(),
                last_name=self.last_name_input.text().strip(),
                document_number=self.document_type_input.text().strip(),
                address=self.address_input.text().strip(),
                notes=self.notes_input.toPlainText().strip(),
                active=int(self.active_checkbox.isChecked())
            )
        if type_index == 1:
            return Customer(
                company=self.company_input.text().strip(),
                first_name=None,
                last_name=None,
                document_number=self.document_type_input.text().strip(),
                address=self.address_input.text().strip(),
                notes=self.notes_input.toPlainText().strip(),
                active=int(self.active_checkbox.isChecked())
            )
        return None

    def _is_input_valid(self, type_index: int) -> bool:
        document = self.document_type_input.text().strip()
        address = self.address_input.text().strip()
        if not document or not address:
            return False
        if type_index == 0:
            first_name = self.first_name_input.text().strip()
            last_name = self.last_name_input.text().strip()
            if not first_name or not last_name:
                return False
        if type_index == 1:
            company = self.company_input.text().strip()
            if not company:
                return False
        return True

    def _is_document_valid(self) -> bool:
        document = self.document_type_input.text().strip()
        if not document:
            return False
        ignored_id = None
        if self.mode != self.ADD_MODE:
            ignored_id = self.customer_data.id
        return not self.customers_widget.customers_model.document_exists(document, ignored_id=ignored_id)

    def _set_add_mode(self) -> None:
        self.created_label.setText(f"{self.created_label_text} {datetime.today().strftime("%d.%m.%Y")}")
        self.subject_type.setCurrentIndex(-1)
        self._apply_type_state()

    def _set_update_mode(self, customer_data: Customer) -> None:
        customer_input_map = {
            self.company_input: customer_data.company,
            self.first_name_input: customer_data.first_name,
            self.last_name_input: customer_data.last_name,
            self.document_type_input: customer_data.document_number,
            self.address_input: customer_data.address,
            self.active_checkbox: customer_data.active,
            self.notes_input: customer_data.notes,
            self.created_label: customer_data.created_at
        }
        self.subject_type.blockSignals(True)
        if customer_data.company is not None:
            self.subject_type.setCurrentIndex(self.COMPANY_INDEX)
        else:
            self.subject_type.setCurrentIndex(self.INDIVIDUAL_INDEX)
        self.subject_type.blockSignals(False)
        self._apply_type_state()
        for widget, value in customer_input_map.items():
            if isinstance(widget, QLabel):
                date = datetime.fromisoformat(value)
                widget.setText(f"{self.created_label_text} {date.strftime("%d.%m.%Y")}")
            if isinstance(widget, QLineEdit):
                widget.setText(value)
            if isinstance(widget, QCheckBox):
                widget.setChecked(value)
            if isinstance(widget, QTextEdit):
                widget.setPlainText(value)
                self.notes_count_label.setText(f"{self.notes_count_text} {len(value)}/{self.NOTES_LENGTH}")

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._update_save_button_state()
        self.adjustSize()
        self.setFixedSize(self.size())
        centre_dialog(self)