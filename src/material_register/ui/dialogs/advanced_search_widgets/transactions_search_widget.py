from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from material_register.db.config.advanced_search_queries_constants import (
    ADVANCED_SEARCH_COLUMNS,
    HAVING_CLAUSE,
    WHERE_CLAUSE,
)
from material_register.domain.adavanced_search_dataclass import (
    AdvancedSearchDataclass,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.styles_constants import INVALID_INPUT_STYLE
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    PAYMENT_CASH,
    PAYMENT_TRANSFER,
    SEARCH_TRANSACTION_MAX_PRICE_VALUE,
    SEARCH_TRANSACTION_MIN_PRICE_VALUE,
    SEARCH_TRANSACTION_NOTES_LENGTH,
    TRANSFER_IN,
    TRANSFER_OUT,
    UI_MARGINS_5,
    UI_SPACING,
)
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.setup.ui_widgets import disable_spinbox_wheel
from material_register.utils.formatting_utils import format_date_to_utc

if TYPE_CHECKING:
    from material_register.ui.dialogs.advanced_search_dialog import AdvancedSearchDialog


class TransactionsSearchWidget(QWidget):
    COLUMN_ROLE = 1
    OPERATOR_ROLE = 2
    VALUE_ROLE = 3

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
        self.transaction_number_checkbox = QCheckBox()
        self.transaction_number_checkbox.setObjectName("transactionNumberCheckbox")
        self.transaction_number_spinbox = QSpinBox()
        date_range_layout = QHBoxLayout()
        date_range_layout.setSpacing(UI_SPACING)
        self.created_at_checkbox = QCheckBox()
        self.created_at_checkbox.setObjectName("createdAtCheckbox")
        self.from_date_label = QLabel()
        self.from_date_label.setObjectName("fromDateLabel")
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        separator_label = QLabel("-")
        self.to_date_label = QLabel()
        self.to_date_label.setObjectName("toDateLabel")
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.transaction_type_checkbox = QCheckBox()
        self.transaction_type_checkbox.setObjectName("transactionTypeCheckBox")
        self.transaction_type_combobox = QComboBox()
        self.transaction_type_combobox.setObjectName("transactionTypeComboBox")
        self.payment_type_checkbox = QCheckBox()
        self.payment_type_checkbox.setObjectName("paymentTypeCheckbox")
        self.payment_type_combobox = QComboBox()
        self.payment_type_combobox.setObjectName("paymentTypeComboBox")
        self.is_invoiced_checkbox = QCheckBox()
        self.is_invoiced_checkbox.setObjectName("isInvoicedCheckbox")
        self.is_invoiced_combobox = QComboBox()
        self.is_invoiced_combobox.setObjectName("isInvoicedComboBox")
        price_layout = QHBoxLayout()
        price_layout.setSpacing(UI_SPACING * 2)
        self.transaction_price_checkbox = QCheckBox()
        self.transaction_price_checkbox.setObjectName("transactionPriceCheckbox")
        self.transaction_price_operator = QComboBox()
        self.transaction_price_operator.setObjectName("transactionPriceOperator")
        self.transaction_price_spinbox = QDoubleSpinBox()
        self.transaction_price_spinbox.setObjectName("transactionPriceSpinbox")
        self.notes_checkbox = QCheckBox()
        self.notes_checkbox.setObjectName("notesCheckbox")
        self.notes_edit = QLineEdit()
        self.notes_edit.setObjectName("notesEdit")
        date_range_layout.addWidget(self.from_date_label)
        date_range_layout.addWidget(self.from_date_edit)
        date_range_layout.addWidget(separator_label)
        date_range_layout.addWidget(self.to_date_label)
        date_range_layout.addWidget(self.to_date_edit)
        date_range_layout.addStretch()
        price_layout.addWidget(self.transaction_price_operator)
        price_layout.addWidget(self.transaction_price_spinbox)
        price_layout.addStretch()
        filters_layout.addWidget(self.transaction_number_checkbox, 0, 0)
        filters_layout.addWidget(self.transaction_number_spinbox, 0, 1)
        filters_layout.addWidget(self.created_at_checkbox, 1, 0)
        filters_layout.addLayout(date_range_layout, 1, 1)
        filters_layout.addWidget(self.transaction_type_checkbox, 2, 0)
        filters_layout.addWidget(self.transaction_type_combobox, 2, 1)
        filters_layout.addWidget(self.payment_type_checkbox, 3, 0)
        filters_layout.addWidget(self.payment_type_combobox, 3, 1)
        filters_layout.addWidget(self.is_invoiced_checkbox, 4, 0)
        filters_layout.addWidget(self.is_invoiced_combobox, 4, 1)
        filters_layout.addWidget(self.transaction_price_checkbox, 5, 0)
        filters_layout.addLayout(price_layout, 5, 1)
        filters_layout.addWidget(self.notes_checkbox, 6, 0)
        filters_layout.addWidget(self.notes_edit, 6, 1)
        filters_layout.setColumnStretch(1, 1)
        main_layout.addLayout(filters_layout)
        main_layout.addStretch()
        filters_widget.setLayout(main_layout)
        return filters_widget

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_spinboxes()
        self._setup_comboboxes()
        self._setup_date_edits()
        self._setup_notes_edit()
        self._setup_property()
        self._setup_user_role()
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
        self.transaction_type_items = ui_texts.get(
            f"{self.transaction_type_combobox.objectName()}Items", []
        )
        self.payment_type_items = ui_texts.get(
            f"{self.payment_type_combobox.objectName()}Items", []
        )
        self.invoiced_items = ui_texts.get(
            f"{self.is_invoiced_combobox.objectName()}Items", []
        )
        self.price_operators = ui_texts.get(
            f"{self.transaction_price_operator.objectName()}Items", []
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
        check_boxes = [
            self.transaction_number_checkbox,
            self.created_at_checkbox,
            self.transaction_type_checkbox,
            self.payment_type_checkbox,
            self.is_invoiced_checkbox,
            self.transaction_price_checkbox,
            self.notes_checkbox,
        ]
        for check_box in check_boxes:
            check_box.toggled.connect(
                lambda checked, selected_check_box=check_box: (
                    self._setup_checkboxes_state(selected_check_box)
                )
            )
        self.from_date_edit.dateChanged.connect(self._update_to_date_minimum)
        self.to_date_edit.dateChanged.connect(self._update_from_date_maximum)
        self.payment_type_checkbox.stateChanged.connect(self._update_invoiced_state)
        self.payment_type_combobox.currentIndexChanged.connect(
            self._update_invoiced_state
        )
        self.is_invoiced_checkbox.stateChanged.connect(self._update_invoiced_state)
        self.notes_edit.textChanged.connect(self._set_notes_style)
        self.reset_button.clicked.connect(
            lambda: self._setup_default_states(reset_values=True)
        )

    def _setup_default_states(self, reset_values: bool = False) -> None:
        widgets = [
            self.transaction_number_spinbox,
            self.from_date_edit,
            self.to_date_edit,
            self.transaction_type_combobox,
            self.payment_type_combobox,
            self.is_invoiced_combobox,
            self.transaction_price_operator,
            self.transaction_price_spinbox,
            self.notes_edit,
        ]
        for widget in widgets:
            widget.setDisabled(True)
        for checkbox in self.findChildren(QCheckBox):
            checkbox.setChecked(False)
        if reset_values:
            for combobox in [
                self.transaction_type_combobox,
                self.payment_type_combobox,
                self.is_invoiced_combobox,
                self.transaction_price_operator,
            ]:
                combobox.setCurrentIndex(0)
            self.transaction_number_spinbox.setValue(
                self.transaction_number_spinbox.minimum()
            )
            self.transaction_price_spinbox.setValue(0)
            self.from_date_edit.setDate(QDate.currentDate())
            self.to_date_edit.setDate(QDate.currentDate())
            self.notes_edit.clear()

    def _setup_spinboxes(self) -> None:
        spinboxes = [self.transaction_number_spinbox, self.transaction_price_spinbox]
        for spinbox in spinboxes:
            if isinstance(spinbox, QSpinBox):
                spinbox.setMinimum(int(SEARCH_TRANSACTION_MIN_PRICE_VALUE))
                spinbox.setMaximum(int(SEARCH_TRANSACTION_MAX_PRICE_VALUE))
            else:
                spinbox.setMinimum(SEARCH_TRANSACTION_MIN_PRICE_VALUE)
                spinbox.setMaximum(SEARCH_TRANSACTION_MAX_PRICE_VALUE)
            spinbox.setAlignment(Qt.AlignmentFlag.AlignRight)
            disable_spinbox_wheel(spinbox)
        self.transaction_price_spinbox.setDecimals(1)
        self.transaction_price_spinbox.setSingleStep(0.1)
        self.transaction_price_spinbox.setGroupSeparatorShown(True)
        self.transaction_price_spinbox.setSuffix(f" {self.price_suffix}")

    def _setup_comboboxes(self) -> None:
        self.transaction_type_combobox.addItems(self.transaction_type_items)
        self.payment_type_combobox.addItems(self.payment_type_items)
        self.is_invoiced_combobox.addItems(self.invoiced_items)
        self.transaction_price_operator.addItems(self.price_operators)

    def _setup_checkboxes_state(self, check_box: QCheckBox) -> None:
        widgets_map = {
            self.transaction_number_checkbox: self.transaction_number_spinbox,
            self.created_at_checkbox: [self.from_date_edit, self.to_date_edit],
            self.transaction_type_checkbox: self.transaction_type_combobox,
            self.payment_type_checkbox: self.payment_type_combobox,
            self.is_invoiced_checkbox: self.is_invoiced_combobox,
            self.transaction_price_checkbox: [
                self.transaction_price_operator,
                self.transaction_price_spinbox,
            ],
            self.notes_checkbox: self.notes_edit,
        }
        if check_box not in widgets_map:
            return
        widgets = widgets_map[check_box]
        if not isinstance(widgets, list):
            widgets = [widgets]
        for widget in widgets:
            widget.setDisabled(not check_box.isChecked())
            if check_box.isChecked() and isinstance(
                widget, (QSpinBox, QDoubleSpinBox, QLineEdit)
            ):
                widget.selectAll()
                widget.setFocus()

    def _setup_date_edits(self) -> None:
        date_edits = [self.from_date_edit, self.to_date_edit]
        for date_edit in date_edits:
            calendar = date_edit.calendarWidget()
            if calendar:
                calendar.setMinimumWidth(250)
                calendar.setMinimumHeight(200)
        today = QDate.currentDate()
        self.from_date_edit.setMaximumDate(today)
        self.from_date_edit.setDate(today)
        self.to_date_edit.setMaximumDate(today)
        self.to_date_edit.setDate(today)

    def _setup_notes_edit(self) -> None:
        self.notes_edit.setMaxLength(SEARCH_TRANSACTION_NOTES_LENGTH)

    def _setup_property(self) -> None:
        self.transaction_number_spinbox.setProperty(
            "column", ADVANCED_SEARCH_COLUMNS["transaction_id"]
        )
        self.transaction_number_spinbox.setProperty("query", "= ?")
        self.notes_edit.setProperty(
            "column", ADVANCED_SEARCH_COLUMNS["transaction_notes"]
        )
        self.notes_edit.setProperty("query", "LIKE ?")
        self.transaction_type_combobox.setProperty(
            "column", ADVANCED_SEARCH_COLUMNS["transaction_type"]
        )
        self.transaction_type_combobox.setProperty("query", "= ?")
        self.payment_type_combobox.setProperty(
            "column", ADVANCED_SEARCH_COLUMNS["transaction_payment_type"]
        )
        self.payment_type_combobox.setProperty("query", "= ?")
        self.is_invoiced_combobox.setProperty(
            "column", ADVANCED_SEARCH_COLUMNS["transaction_is_invoiced"]
        )
        self.is_invoiced_combobox.setProperty("query", "= ?")
        self.transaction_price_spinbox.setProperty(
            "column", ADVANCED_SEARCH_COLUMNS["total"]
        )

    def _setup_user_role(self) -> None:
        user_role_map = {
            self.transaction_type_combobox: [TRANSFER_IN, TRANSFER_OUT],
            self.payment_type_combobox: [PAYMENT_CASH, PAYMENT_TRANSFER],
            self.is_invoiced_combobox: [1, 0],
            self.transaction_price_operator: ["< ?", "= ?", "> ?"],
        }
        for widget, user_roles in user_role_map.items():
            for index, value in enumerate(user_roles):
                widget.setItemData(index, value, Qt.ItemDataRole.UserRole)

    def _update_to_date_minimum(self, date: QDate) -> None:
        self.to_date_edit.setMinimumDate(date)

    def _update_from_date_maximum(self, date: QDate) -> None:
        self.from_date_edit.setMaximumDate(date)

    def _update_invoiced_state(self) -> None:
        cash_selected = (
            self.payment_type_checkbox.isChecked()
            and self.payment_type_combobox.currentIndex() == 0
        )
        if cash_selected:
            self.is_invoiced_checkbox.setChecked(False)
        self.is_invoiced_checkbox.setDisabled(cash_selected)
        self.is_invoiced_combobox.setDisabled(
            cash_selected or not self.is_invoiced_checkbox.isChecked()
        )

    def _set_notes_style(self) -> None:
        text = self.notes_edit.text().strip()
        if len(text) >= SEARCH_TRANSACTION_NOTES_LENGTH:
            self.notes_edit.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            self.notes_edit.setStyleSheet("")

    def _get_property_filters(self) -> list[AdvancedSearchDataclass]:
        filters_map = {
            self.transaction_number_checkbox: self.transaction_number_spinbox,
            self.notes_checkbox: self.notes_edit,
        }
        property_filters = []
        for state, widget in filters_map.items():
            if state.isChecked():
                if isinstance(widget, QSpinBox):
                    property_filters.append(
                        AdvancedSearchDataclass(
                            clause=WHERE_CLAUSE,
                            column_name=widget.property("column"),
                            query=widget.property("query"),
                            value=widget.value(),
                        )
                    )
                if isinstance(widget, QLineEdit):
                    property_filters.append(
                        AdvancedSearchDataclass(
                            clause=WHERE_CLAUSE,
                            column_name=widget.property("column"),
                            query=widget.property("query"),
                            value=f"%{widget.text().strip()}%",
                        )
                    )
        return property_filters

    def _get_date_filters(self) -> list[AdvancedSearchDataclass]:
        date_filters = []
        from_date = format_date_to_utc(self.from_date_edit.date())
        to_date = format_date_to_utc(self.to_date_edit.date(), end_of_day=True)
        if self.created_at_checkbox.isChecked():
            date_filters.append(
                AdvancedSearchDataclass(
                    clause=WHERE_CLAUSE,
                    column_name=ADVANCED_SEARCH_COLUMNS["transaction_created_at"],
                    query="BETWEEN ? AND ?",
                    value=(from_date, to_date),
                )
            )
        return date_filters

    def _get_user_role_filters(self) -> list[AdvancedSearchDataclass]:
        user_role_map = {
            self.transaction_type_checkbox: self.transaction_type_combobox,
            self.payment_type_checkbox: self.payment_type_combobox,
            self.is_invoiced_checkbox: self.is_invoiced_combobox,
            self.transaction_price_checkbox: self.transaction_price_spinbox,
        }
        user_role_filters = []
        for state, widget in user_role_map.items():
            if state.isChecked():
                if isinstance(widget, QComboBox):
                    user_role_filters.append(
                        AdvancedSearchDataclass(
                            clause=WHERE_CLAUSE,
                            column_name=widget.property("column"),
                            query=widget.property("query"),
                            value=widget.currentData(Qt.ItemDataRole.UserRole),
                        )
                    )
                if isinstance(widget, QDoubleSpinBox):
                    user_role_filters.append(
                        AdvancedSearchDataclass(
                            clause=HAVING_CLAUSE,
                            column_name=widget.property("column"),
                            query=self.transaction_price_operator.currentData(
                                Qt.ItemDataRole.UserRole
                            ),
                            value=widget.value(),
                        )
                    )
        return user_role_filters

    def get_filters_data(self) -> list[AdvancedSearchDataclass]:
        filters_data = []
        filters = [
            self._get_property_filters(),
            self._get_date_filters(),
            self._get_user_role_filters(),
        ]
        for section_filters in filters:
            if section_filters:
                filters_data.extend(section_filters)
        return filters_data
