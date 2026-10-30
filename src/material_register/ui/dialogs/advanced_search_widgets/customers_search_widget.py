from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.styles_constants import INVALID_INPUT_STYLE
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    SEARCH_TRANSACTION_NOTES_LENGTH,
    UI_MARGINS_5,
    UI_SPACING,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.advanced_search_dialog import AdvancedSearchDialog


class CustomersSearchWidget(QWidget):
    WIDTH = 300
    PREFIX = "prefix"
    CONTAINS = "contains"
    SUFFIX = "suffix"

    def __init__(self, advanced_search_dialog: "AdvancedSearchDialog") -> None:
        super().__init__(advanced_search_dialog)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(0, 0, 0, 0)
        filters_section = self._create_filters_section()
        buttons_layout = QHBoxLayout()
        self.reset_button = QPushButton()
        self.reset_button.setObjectName("resetButton")
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addStretch()
        main_layout.addWidget(filters_section, 1)
        main_layout.addLayout(buttons_layout)
        return main_layout

    def _create_filters_section(self) -> QWidget:
        filters_widget = QWidget()
        main_layout = QVBoxLayout()
        filters_layout = QGridLayout()
        filters_layout.setHorizontalSpacing(UI_SPACING * 4)
        filters_layout.setVerticalSpacing(UI_SPACING)
        filters_layout.setContentsMargins(*UI_MARGINS_5)
        self.subject_type_checkbox = QCheckBox()
        self.subject_type_checkbox.setObjectName("subjectTypeCheckBox")
        self.subject_type_combo_box = QComboBox()
        self.subject_type_combo_box.setObjectName("subjectTypeComboBox")
        self.company_name_checkbox = QCheckBox()
        self.company_name_checkbox.setObjectName("companyNameCheckBox")
        self.company_name_operator = QComboBox()
        self.company_name_operator.setObjectName("companyNameOperator")
        self.company_name_edit = QLineEdit()
        self.company_name_edit.setObjectName("companyNameEdit")
        self.first_name_checkbox = QCheckBox()
        self.first_name_checkbox.setObjectName("firstNameCheckBox")
        self.first_name_operator = QComboBox()
        self.first_name_operator.setObjectName("firstNameOperator")
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setObjectName("firstNameEdit")
        self.last_name_checkbox = QCheckBox()
        self.last_name_checkbox.setObjectName("lastNameCheckBox")
        self.last_name_operator = QComboBox()
        self.last_name_operator.setObjectName("lastNameOperator")
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setObjectName("lastNameEdit")
        self.document_checkbox = QCheckBox()
        self.document_checkbox.setObjectName("documentCheckbox")
        self.document_operator = QComboBox()
        self.document_operator.setObjectName("documentOperator")
        self.document_edit = QLineEdit()
        self.document_edit.setObjectName("documentEdit")
        self.address_checkbox = QCheckBox()
        self.address_checkbox.setObjectName("addressCheckbox")
        self.address_operator = QComboBox()
        self.address_operator.setObjectName("addressOperator")
        self.address_edit = QLineEdit()
        self.address_edit.setObjectName("addressEdit")
        self.active_checkbox = QCheckBox()
        self.active_checkbox.setObjectName("activeCheckbox")
        self.active_combo_box = QComboBox()
        self.active_combo_box.setObjectName("activeComboBox")
        self.notes_checkbox = QCheckBox()
        self.notes_checkbox.setObjectName("notesCheckbox")
        self.notes_edit = QLineEdit()
        self.notes_edit.setObjectName("notesEdit")
        filters_layout.addWidget(self.subject_type_checkbox, 0, 0)
        filters_layout.addWidget(self.subject_type_combo_box, 0, 1)
        filters_layout.addWidget(self.company_name_checkbox, 1, 0)
        filters_layout.addWidget(self.company_name_operator, 1, 1)
        filters_layout.addWidget(self.company_name_edit, 1, 2)
        filters_layout.addWidget(self.first_name_checkbox, 2, 0)
        filters_layout.addWidget(self.first_name_operator, 2, 1)
        filters_layout.addWidget(self.first_name_edit, 2, 2)
        filters_layout.addWidget(self.last_name_checkbox, 3, 0)
        filters_layout.addWidget(self.last_name_operator, 3, 1)
        filters_layout.addWidget(self.last_name_edit, 3, 2)
        filters_layout.addWidget(self.document_checkbox, 4, 0)
        filters_layout.addWidget(self.document_operator, 4, 1)
        filters_layout.addWidget(self.document_edit, 4, 2)
        filters_layout.addWidget(self.address_checkbox, 5, 0)
        filters_layout.addWidget(self.address_operator, 5, 1)
        filters_layout.addWidget(self.address_edit, 5, 2)
        filters_layout.addWidget(self.active_checkbox, 6, 0)
        filters_layout.addWidget(self.active_combo_box, 6, 1)
        filters_layout.addWidget(self.notes_checkbox, 7, 0)
        filters_layout.addWidget(self.notes_edit, 7, 1, 1, 2)
        main_layout.addLayout(filters_layout)
        filters_widget.setLayout(main_layout)
        return filters_widget

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_comboboxes()
        self._setup_line_edits()
        self._setup_default_states()

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
        self.subject_type_items = ui_texts.get(
            f"{self.subject_type_combo_box.objectName()}Items", []
        )
        self.company_name_operators = ui_texts.get(
            f"{self.company_name_operator.objectName()}Items", []
        )
        self.first_name_operators = ui_texts.get(
            f"{self.first_name_operator.objectName()}Items", []
        )
        self.last_name_operators = ui_texts.get(
            f"{self.last_name_operator.objectName()}Items", []
        )
        self.document_operators = ui_texts.get(
            f"{self.document_operator.objectName()}Items", []
        )
        self.address_operators = ui_texts.get(
            f"{self.address_operator.objectName()}Items", []
        )
        self.active_items = ui_texts.get(
            f"{self.active_combo_box.objectName()}Items", []
        )
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
        check_boxes = self.findChildren(QCheckBox)
        for check_box in check_boxes:
            check_box.toggled.connect(
                lambda _, selected_check_box=check_box: self._setup_checkboxes_state(
                    selected_check_box
                )
            )
        self.subject_type_checkbox.toggled.connect(self._update_customer_state)
        self.subject_type_combo_box.currentIndexChanged.connect(
            self._update_customer_state
        )
        self.company_name_checkbox.toggled.connect(self._update_customer_state)
        self.first_name_checkbox.toggled.connect(self._update_customer_state)
        self.last_name_checkbox.toggled.connect(self._update_customer_state)
        self.reset_button.clicked.connect(
            lambda: self._setup_default_states(reset_values=True)
        )

    def _setup_default_states(self, reset_values: bool = False) -> None:
        widgets = self.findChildren(QComboBox) + self.findChildren(QLineEdit)
        for widget in widgets:
            widget.setDisabled(True)
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(False)
        if reset_values:
            for widget in self.findChildren(QComboBox):
                widget.setCurrentIndex(0)
            for widget in self.findChildren(QLineEdit):
                widget.clear()

    def _setup_comboboxes(self) -> None:
        self.subject_type_combo_box.addItems(self.subject_type_items)
        self.company_name_operator.addItems(self.company_name_operators)
        self.first_name_operator.addItems(self.first_name_operators)
        self.last_name_operator.addItems(self.last_name_operators)
        self.document_operator.addItems(self.document_operators)
        self.address_operator.addItems(self.address_operators)
        self.active_combo_box.addItems(self.active_items)

    def _setup_checkboxes_state(self, check_box: QCheckBox) -> None:
        widgets_map = {
            self.subject_type_checkbox: self.subject_type_combo_box,
            self.company_name_checkbox: [
                self.company_name_operator,
                self.company_name_edit,
            ],
            self.first_name_checkbox: [self.first_name_operator, self.first_name_edit],
            self.last_name_checkbox: [self.last_name_operator, self.last_name_edit],
            self.document_checkbox: [self.document_operator, self.document_edit],
            self.address_checkbox: [self.address_operator, self.address_edit],
            self.active_checkbox: self.active_combo_box,
            self.notes_checkbox: self.notes_edit,
        }
        if not check_box in widgets_map:
            return
        widgets = widgets_map[check_box]
        if not isinstance(widgets, list):
            widgets = [widgets]
        for widget in widgets:
            widget.setDisabled(not check_box.isChecked())
            if check_box.isChecked() and isinstance(widget, QLineEdit):
                widget.selectAll()
                widget.setFocus()

    def _setup_line_edits(self) -> None:
        for edit in self.findChildren(QLineEdit):
            if edit.objectName() != self.notes_edit.objectName():
                edit.setFixedWidth(self.WIDTH)
            edit.setMaxLength(SEARCH_TRANSACTION_NOTES_LENGTH)

    def _setup_user_role(self) -> None:
        like_operators = [self.PREFIX, self.CONTAINS, self.SUFFIX]
        user_role_map = {
            self.subject_type_combo_box: [1, 0],
            self.company_name_operator: like_operators,
            self.first_name_operator: like_operators,
            self.last_name_operator: like_operators,
            self.document_operator: like_operators,
            self.address_operator: like_operators,
            self.active_combo_box: [1, 0],
        }
        for widget, user_role in user_role_map.items():
            for index, value in enumerate(user_role):
                widget.setItemData(index, value, Qt.ItemDataRole.UserRole)

    def _update_customer_state(self) -> None:
        subject_type_enabled = self.subject_type_checkbox.isChecked()
        company_selected = (
            subject_type_enabled and self.subject_type_combo_box.currentIndex() == 1
        )
        if subject_type_enabled:
            if company_selected:
                self.first_name_checkbox.setChecked(False)
                self.last_name_checkbox.setChecked(False)
            else:
                self.company_name_checkbox.setChecked(False)
        elif self.company_name_checkbox.isChecked():
            self.first_name_checkbox.setChecked(False)
            self.last_name_checkbox.setChecked(False)
        elif (
            self.first_name_checkbox.isChecked() or self.last_name_checkbox.isChecked()
        ):
            self.company_name_checkbox.setChecked(False)
        name_selected = (
            self.first_name_checkbox.isChecked() or self.last_name_checkbox.isChecked()
        )
        company_name_selected = self.company_name_checkbox.isChecked()
        self.company_name_checkbox.setDisabled(
            name_selected or (subject_type_enabled and not company_selected)
        )
        self.first_name_checkbox.setDisabled(company_name_selected or company_selected)
        self.last_name_checkbox.setDisabled(company_name_selected or company_selected)
        if subject_type_enabled:
            if company_name_selected:
                self.subject_type_combo_box.setCurrentIndex(1)
            elif name_selected:
                self.subject_type_combo_box.setCurrentIndex(0)

    def _set_notes_style(self) -> None:
        text = self.notes_edit.text().strip()
        if len(text) >= SEARCH_TRANSACTION_NOTES_LENGTH:
            self.notes_edit.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            self.notes_edit.setStyleSheet("")
