from pathlib import Path

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QDate, QStandardPaths, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator, QFontMetrics, QResizeEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QLabel, \
    QSizePolicy, QGroupBox, QButtonGroup, QRadioButton, QDateEdit, QComboBox, QFileDialog, QDoubleSpinBox, QScrollArea, \
    QCheckBox

from material_register.config.ui_constants import EXPORT_PRICE_MIN_VALUE, EXPORT_PRICE_MAX_VALUE
from material_register.controllers.export_controller import ExportController
from material_register.db.utils.date_filters import get_filter_range
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.styles import INVALID_INPUT_STYLE
from material_register.ui.setup.ui_settings import UiSettings
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class ExportWidget(QWidget):
    WIDTH = 400
    SPACING = 20

    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.export_controller = ExportController(self)
        self.current_path = ""
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        group_widget = QWidget()
        group_layout = QVBoxLayout(group_widget)
        group_layout.setSpacing(self.SPACING)
        branch_group = self._create_branch_group()
        path_name_group = self._create_path_name_group()
        date_options_group = self._create_date_options_group()
        financial_data_group = self._create_financial_data_group()
        export_options_group = self._create_export_options_group()
        other_settings_group = self._create_other_settings_group()
        group_layout.addWidget(branch_group)
        group_layout.addWidget(path_name_group)
        group_layout.addWidget(date_options_group)
        group_layout.addWidget(financial_data_group)
        group_layout.addWidget(export_options_group)
        group_layout.addWidget(other_settings_group)
        export_action_group = self._create_export_action_group()
        scroll_area.setWidget(group_widget)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(export_action_group)
        return main_layout

    def _create_branch_group(self) -> QGroupBox:
        self.branch_group_box = QGroupBox()
        self.branch_group_box.setObjectName("branchGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        form_layout = QFormLayout()
        self.branch_name_label = QLabel()
        self.branch_name_label.setObjectName("branchNameLabel")
        self.branch_name_line_edit = QLineEdit()
        self.branch_name_line_edit.setObjectName("branchNameLineEdit")
        self.branch_name_line_edit.setMinimumWidth(self.WIDTH)
        self.branch_name_line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        form_layout.addRow(self.branch_name_label, self.branch_name_line_edit)
        main_layout.addLayout(form_layout)
        self.branch_group_box.setLayout(main_layout)
        return self.branch_group_box

    def _create_path_name_group(self) -> QGroupBox:
        self.path_name_group_box = QGroupBox()
        self.path_name_group_box.setObjectName("pathNameGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        file_type_layout = QHBoxLayout()
        self.file_type_label = QLabel()
        self.file_type_label.setObjectName("fileTypeLabel")
        self.file_type_combobox = QComboBox()
        self.file_type_combobox.setObjectName("fileTypeComboBox")
        form_layout = QFormLayout()
        self.path_label = QLabel()
        self.path_label.setObjectName("pathLabel")
        self.path_line_edit = QLineEdit()
        self.path_line_edit.setObjectName("pathLineEdit")
        self.path_line_edit.setMinimumWidth(self.WIDTH)
        self.path_line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.path_button = QPushButton()
        self.path_button.setObjectName("pathButton")
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_line_edit)
        path_layout.addWidget(self.path_button)
        self.file_name_label = QLabel()
        self.file_name_label.setObjectName("fileNameLabel")
        self.file_name_line_edit = QLineEdit()
        self.file_name_line_edit.setObjectName("fileNameLineEdit")
        self.file_name_line_edit.setMinimumWidth(self.WIDTH)
        self.file_name_line_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.suffix_label = QLabel()
        self.suffix_label.setObjectName("suffixLabel")
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.file_name_line_edit)
        name_layout.addWidget(self.suffix_label)
        file_type_layout.addStretch()
        file_type_layout.addWidget(self.file_type_label)
        file_type_layout.addWidget(self.file_type_combobox)
        file_type_layout.addStretch()
        form_layout.addRow(self.path_label, path_layout)
        form_layout.addRow(self.file_name_label, name_layout)
        main_layout.addLayout(file_type_layout)
        main_layout.addLayout(form_layout)
        self.path_name_group_box.setLayout(main_layout)
        return self.path_name_group_box

    def _create_date_options_group(self) -> QGroupBox:
        self.date_options_group_box = QGroupBox()
        self.date_options_group_box.setObjectName("dateOptionsGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        self.time_button_group = QButtonGroup()
        standard_time_layout = QHBoxLayout()
        self.today_radio_button = QRadioButton()
        self.today_radio_button.setObjectName("todayRadioButton")
        self.week_radio_button = QRadioButton()
        self.week_radio_button.setObjectName("weekRadioButton")
        self.month_radio_button = QRadioButton()
        self.month_radio_button.setObjectName("monthRadioButton")
        self.year_radio_button = QRadioButton()
        self.year_radio_button.setObjectName("yearRadioButton")
        custom_time_layout = QHBoxLayout()
        custom_time_layout.setSpacing(self.SPACING)
        self.custom_radio_button = QRadioButton()
        self.custom_radio_button.setObjectName("customRadioButton")
        from_to_layout = QHBoxLayout()
        from_to_layout.setSpacing(self.SPACING // 2)
        self.from_date_label = QLabel()
        self.from_date_label.setObjectName("fromDateLabel")
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        separator_label = QLabel("-")
        self.from_date_edit.setObjectName("fromDateEdit")
        self.to_date_label = QLabel()
        self.to_date_label.setObjectName("toDateLabel")
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setObjectName("toDateEdit")
        self.time_button_group.addButton(self.today_radio_button)
        self.time_button_group.addButton(self.week_radio_button)
        self.time_button_group.addButton(self.month_radio_button)
        self.time_button_group.addButton(self.year_radio_button)
        self.time_button_group.addButton(self.custom_radio_button)
        standard_time_layout.addWidget(self.today_radio_button)
        standard_time_layout.addWidget(self.week_radio_button)
        standard_time_layout.addWidget(self.month_radio_button)
        standard_time_layout.addWidget(self.year_radio_button)
        standard_time_layout.addStretch()
        from_to_layout.addWidget(self.from_date_label)
        from_to_layout.addWidget(self.from_date_edit)
        from_to_layout.addWidget(separator_label)
        from_to_layout.addWidget(self.to_date_label)
        from_to_layout.addWidget(self.to_date_edit)
        custom_time_layout.addWidget(self.custom_radio_button)
        custom_time_layout.addLayout(from_to_layout)
        custom_time_layout.addStretch()
        main_layout.addLayout(standard_time_layout)
        main_layout.addLayout(custom_time_layout)
        self.date_options_group_box.setLayout(main_layout)
        return self.date_options_group_box

    def _create_financial_data_group(self) -> QGroupBox:
        self.financial_data_group_box = QGroupBox()
        self.financial_data_group_box.setObjectName("financialDataGroupBox")
        main_layout = QHBoxLayout()
        form_layout = QFormLayout()
        form_layout.setSpacing(self.SPACING)
        self.opening_balance_label = QLabel()
        self.opening_balance_label.setObjectName("openingBalanceLabel")
        self.opening_balance_spinbox  =QDoubleSpinBox()
        self.opening_balance_spinbox.setObjectName("openingBalanceSpinbox")
        self.income_label = QLabel()
        self.income_label.setObjectName("incomeLabel")
        self.income_spinbox = QDoubleSpinBox()
        self.income_spinbox.setObjectName("incomeSpinbox")
        self.expense_label = QLabel()
        self.expense_label.setObjectName("expenseLabel")
        self.expense_spinbox = QDoubleSpinBox()
        self.expense_spinbox.setObjectName("expenseSpinbox")
        form_layout.addRow(self.opening_balance_label, self.opening_balance_spinbox)
        form_layout.addRow(self.income_label, self.income_spinbox)
        form_layout.addRow(self.expense_label, self.expense_spinbox)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        self.financial_data_group_box.setLayout(main_layout)
        return self.financial_data_group_box

    def _create_export_options_group(self) -> QGroupBox:
        self.export_options_group_box = QGroupBox()
        self.export_options_group_box.setObjectName("exportOptionsGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        self.no_action_radio_button = QRadioButton()
        self.no_action_radio_button.setObjectName("noActionRadioButton")
        self.open_folder_radio_button = QRadioButton()
        self.open_folder_radio_button.setObjectName("openFolderRadioButton")
        self.open_file_radio_button = QRadioButton()
        self.open_file_radio_button.setObjectName("openFileRadioButton")
        main_layout.addWidget(self.no_action_radio_button)
        main_layout.addWidget(self.open_folder_radio_button)
        main_layout.addWidget(self.open_file_radio_button)
        main_layout.addStretch()
        self.export_options_group_box.setLayout(main_layout)
        return self.export_options_group_box

    def _create_other_settings_group(self) -> QGroupBox:
        self.other_settings_group_box = QGroupBox()
        self.other_settings_group_box.setObjectName("otherSettingsGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        self.use_last_options_checkbox = QCheckBox()
        self.use_last_options_checkbox.setObjectName("useLastOptionsCheckbox")
        self.save_last_opening_balance_checkbox = QCheckBox()
        self.save_last_opening_balance_checkbox.setObjectName("saveLastOpeningBalanceCheckbox")
        main_layout.addWidget(self.use_last_options_checkbox)
        main_layout.addWidget(self.save_last_opening_balance_checkbox)
        self.other_settings_group_box.setLayout(main_layout)
        return self.other_settings_group_box

    def _create_export_action_group(self) -> QGroupBox:
        self.export_action_group_box = QGroupBox()
        self.export_action_group_box.setObjectName("exportActionGroupBox")
        main_layout = QHBoxLayout()
        main_layout.setSpacing(self.SPACING)
        self.export_button = QPushButton()
        self.export_button.setObjectName("exportButton")
        main_layout.addStretch()
        main_layout.addWidget(self.export_button)
        main_layout.addStretch()
        self.export_action_group_box.setLayout(main_layout)
        return self.export_action_group_box

    def _setup_ui(self) -> None:
        widgets = self.findChildren(QWidget)
        self._setup_texts(widgets)
        self._setup_spinboxes()
        self.apply_settings()
        self._set_folder_path()
        self._set_file_suffix()
        self._set_validators()
        self._apply_date_state()
        self._setup_date_edits()
        self._set_required_style()
        self._apply_export_action_state()

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.folder_dialog_title = ui_texts.get("folderDialogTitle", "Select Export Folder")
        self.price_suffix = ui_texts.get("priceSuffix", "")
        type_items = ui_texts.get(f"{self.file_type_combobox.objectName()}Items", [])
        if not type_items:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.file_type_combobox.addItems(type_items)
        if UiTexts.set_ui_texts(self, widgets):
            self.default_name = ui_texts.get(f"{self.file_name_line_edit.objectName()}Text", "Export")
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def apply_settings(self) -> None:
        if not UiSettings.set_ui_settings("export", self.findChildren(QWidget)):
            ErrorHandler.handle_error(f"Settings load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_settings_error = "CONFIG_LOAD_FAILED"
            return
        self._set_folder_path()
        if not self.file_name_line_edit.text().strip():
            today = QDate.currentDate()
            self.file_name_line_edit.setText(f"{self.default_name}_{today.year()}_{today.month()}_{today.day()}")
        self.today_radio_button.setChecked(True)

    def _create_connection(self) -> None:
        date_radiobuttons = [self.today_radio_button, self.week_radio_button, self.month_radio_button,
                             self.year_radio_button, self.custom_radio_button]
        self.branch_name_line_edit.textChanged.connect(self._on_text_or_value_changed)
        self.file_type_combobox.currentIndexChanged.connect(self._set_file_suffix)
        self.file_name_line_edit.textChanged.connect(self._on_text_or_value_changed)
        self.path_button.clicked.connect(self._select_export_folder)
        for radio_button in date_radiobuttons:
            radio_button.toggled.connect(self._apply_date_state)
        self.from_date_edit.dateChanged.connect(self._update_to_date_minimum)
        self.to_date_edit.dateChanged.connect(self._update_from_date_maximum)
        self.opening_balance_spinbox.valueChanged.connect(self._on_text_or_value_changed)
        self.export_button.clicked.connect(self.export_controller.start_export)

    def _setup_spinboxes(self) -> None:
        spinboxes = [self.opening_balance_spinbox, self.income_spinbox, self.expense_spinbox]
        for spinbox in spinboxes:
            spinbox.setMinimum(EXPORT_PRICE_MIN_VALUE)
            spinbox.setMaximum(EXPORT_PRICE_MAX_VALUE)
            spinbox.setDecimals(1)
            spinbox.setSingleStep(0.1)
            spinbox.setGroupSeparatorShown(True)
            if self.price_suffix:
                spinbox.setSuffix(f" {self.price_suffix}")

    def _set_validators(self) -> None:
        name_validator = QRegularExpressionValidator(QRegularExpression(r"[A-Za-zÀ-ž0-9_\- ]{1,30}"))
        self.branch_name_line_edit.setValidator(name_validator)
        self.file_name_line_edit.setValidator(name_validator)

    def _set_folder_path(self) -> None:
        if not self.path_line_edit.text().strip():
            self.current_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
        else:
            self.current_path = self.path_line_edit.text().strip()
        self._set_elided_path(self.current_path)
        self.path_line_edit.setToolTip(self.current_path)
        self.path_line_edit.setToolTipDuration(3000)
        self.path_line_edit.setReadOnly(True)

    def _set_file_suffix(self) -> None:
        self.suffix_label.setText(ExportWidget._get_file_suffix(self.file_type_combobox.currentText()))

    def _on_text_or_value_changed(self) -> None:
        self._apply_export_action_state()
        self._set_required_style()

    def _apply_date_state(self) -> None:
        if self.custom_radio_button.isChecked():
            self.from_date_edit.setEnabled(True)
            self.to_date_edit.setEnabled(True)
        else:
            self.from_date_edit.setEnabled(False)
            self.to_date_edit.setEnabled(False)

    def _apply_export_action_state(self) -> None:
        if (self.branch_name_line_edit.text().strip() != ""
                and self.file_name_line_edit.text().strip() != ""
                and self.opening_balance_spinbox.value() > 0.0):
            self.export_button.setEnabled(True)
        else:
            self.export_button.setEnabled(False)

    def _setup_date_edits(self) -> None:
        today = QDate.currentDate()
        start_of_year = QDate(today.year(), 1, 1)
        self.from_date_edit.setMinimumDate(start_of_year)
        self.from_date_edit.setMaximumDate(today)
        self.from_date_edit.setDate(start_of_year)
        self.to_date_edit.setMinimumDate(start_of_year)
        self.to_date_edit.setMaximumDate(today)
        self.to_date_edit.setDate(today)

    def _update_to_date_minimum(self, date: QDate) -> None:
        self.to_date_edit.setMinimumDate(date)

    def _update_from_date_maximum(self, date: QDate) -> None:
        self.from_date_edit.setMaximumDate(date)

    def _set_required_style(self) -> None:
        if self.branch_name_line_edit.text().strip() == "":
            self.branch_name_line_edit.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            self.branch_name_line_edit.setStyleSheet("")
        if self.file_name_line_edit.text().strip() == "":
            self.file_name_line_edit.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            self.file_name_line_edit.setStyleSheet("")
        if self.opening_balance_spinbox.value() == 0.0:
            self.opening_balance_spinbox.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            self.opening_balance_spinbox.setStyleSheet("")

    def _set_elided_path(self, path: str) -> None:
        metrics = QFontMetrics(self.path_line_edit.font())
        elided_path = metrics.elidedText(path, Qt.TextElideMode.ElideMiddle, self.path_line_edit.width())
        self.path_line_edit.setText(elided_path)

    def _select_export_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, self.folder_dialog_title, self.current_path)
        if folder:
            self.current_path = folder
            self._set_elided_path(self.current_path)
            self.path_line_edit.setToolTip(folder)

    def _get_full_path(self) -> Path:
        return (Path(self.current_path) / self.file_name_line_edit.text().strip()).with_suffix(self.suffix_label.text())

    def _get_date_interval(self) -> tuple[str, str]:
        date_map = {
            self.today_radio_button: "today",
            self.week_radio_button: "week",
            self.month_radio_button: "month",
            self.year_radio_button: "year",
        }
        for key in date_map:
            if key.isChecked():
                date_range = get_filter_range(date_map[key])
                if date_range is not None:
                    return date_range
        date_range = (self.from_date_edit.date().toString("yyyy-MM-dd 00:00:00"),
                      self.to_date_edit.date().toString("yyyy-MM-dd 23:59:59"))
        return date_range

    @staticmethod
    def _get_file_suffix(file_type: str) -> str:
        file_map = {
            "Excel": ".xlsx",
        }
        return file_map[file_type]

    @staticmethod
    def _normalize_value(value: float) -> float:
        return float(f"{value:.1f}")

    def get_export_data(self) -> dict[str, Path | str | float | bool]:
        from_date, to_date = self._get_date_interval()
        return {
            "branchNameLineEdit": self.branch_name_line_edit.text().strip(),
            "pathLineEdit": self._get_full_path(),
            "fileNameLineEdit": self.file_name_line_edit.text().strip(),
            "from_date": from_date,
            "to_date": to_date,
            "opening_balance": ExportWidget._normalize_value(self.opening_balance_spinbox.value()),
            "income": ExportWidget._normalize_value(self.income_spinbox.value()),
            "expense": ExportWidget._normalize_value(self.expense_spinbox.value()),
            "noActionRadioButton": self.no_action_radio_button.isChecked(),
            "openFolderRadioButton": self.open_folder_radio_button.isChecked(),
            "openFileRadioButton": self.open_file_radio_button.isChecked(),
            "useLastOptionsCheckbox": self.use_last_options_checkbox.isChecked(),
            "saveLastOpeningBalanceCheckbox": self.save_last_opening_balance_checkbox.isChecked()
        }

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        if self.current_path:
            self._set_elided_path(self.current_path)