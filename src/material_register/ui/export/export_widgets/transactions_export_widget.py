from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, QRegularExpression, QStandardPaths, Qt, QTimer
from PySide6.QtGui import QFontMetrics, QRegularExpressionValidator, QResizeEvent
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QCompleter,
    QDateEdit,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from material_register.config.ui_constants import (
    EXPORT_TYPE_TRANSACTIONS,
    TRANSFER_IN,
    TRANSFER_OUT,
)
from material_register.controllers.export_controllers.transactions_export_controller import (
    TransactionsExportController,
)
from material_register.db.models.customers_completer_model import (
    CustomersCompleterModel,
)
from material_register.services.db_cache import DbCache
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.styles import INVALID_INPUT_STYLE
from material_register.ui.setup.ui_settings import UiSettings
from material_register.ui.setup.ui_texts import UiTexts
from material_register.utils.date_filters import get_filter_range

if TYPE_CHECKING:
    from material_register.ui.export.export_widget import ExportWidget


class TransactionsExportWidget(QWidget):
    WIDTH = 400
    SPACING = 20

    def __init__(self, export_widget: "ExportWidget") -> None:
        super().__init__(export_widget)
        self.completer_model = CustomersCompleterModel(DbCache.customers)
        self.transactions_export_controller = TransactionsExportController(self)
        self.current_path = Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DocumentsLocation
            )
        )
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
        transaction_options_group = self._create_transaction_options_group()
        export_options_group = self._create_export_options_group()
        other_settings_group = self._create_other_settings_group()
        group_layout.addWidget(branch_group)
        group_layout.addWidget(path_name_group)
        group_layout.addWidget(date_options_group)
        group_layout.addWidget(transaction_options_group)
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
        self.branch_name_line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
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
        self.path_line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
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
        self.file_name_line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.file_name_line_edit)
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
        month_split = QHBoxLayout()
        self.month_split_checkbox = QCheckBox()
        self.month_split_checkbox.setObjectName("monthSplitCheckbox")
        self.month_split_checkbox.setEnabled(False)
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
        month_split.addWidget(self.month_split_checkbox)
        month_split.addStretch()
        main_layout.addLayout(standard_time_layout)
        main_layout.addLayout(custom_time_layout)
        main_layout.addLayout(month_split)
        self.date_options_group_box.setLayout(main_layout)
        return self.date_options_group_box

    def _create_transaction_options_group(self) -> QGroupBox:
        self.transaction_options_group_box = QGroupBox()
        self.transaction_options_group_box.setObjectName("transactionOptionsGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        customer_layout = QHBoxLayout()
        self.customer_label = QLabel()
        self.customer_label.setObjectName("customerLabel")
        self.customer_combobox = QComboBox()
        self.customer_combobox.setObjectName("customerComboBox")
        self.customer_combobox.setMinimumWidth(self.WIDTH)
        self.customer_combobox.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        customer_layout.addWidget(self.customer_label)
        customer_layout.addWidget(self.customer_combobox)
        customer_layout.addStretch()
        transaction_type_layout = QHBoxLayout()
        transaction_type_layout.setSpacing(self.SPACING)
        self.transaction_type_label = QLabel()
        self.transaction_type_label.setObjectName("transactionTypeLabel")
        self.transaction_type_button_group = QButtonGroup()
        self.all_radio_button = QRadioButton()
        self.all_radio_button.setObjectName("allRadioButton")
        self.in_radio_button = QRadioButton()
        self.in_radio_button.setObjectName("inRadioButton")
        self.out_radio_button = QRadioButton()
        self.out_radio_button.setObjectName("outRadioButton")
        self.transaction_type_button_group.addButton(self.all_radio_button)
        self.transaction_type_button_group.addButton(self.in_radio_button)
        self.transaction_type_button_group.addButton(self.out_radio_button)
        transaction_type_layout.addWidget(self.transaction_type_label)
        transaction_type_layout.addWidget(self.all_radio_button)
        transaction_type_layout.addWidget(self.in_radio_button)
        transaction_type_layout.addWidget(self.out_radio_button)
        transaction_type_layout.addStretch()
        main_layout.addLayout(customer_layout)
        main_layout.addLayout(transaction_type_layout)
        self.transaction_options_group_box.setLayout(main_layout)
        return self.transaction_options_group_box

    def _create_export_options_group(self) -> QGroupBox:
        self.export_options_group_box = QGroupBox()
        self.export_options_group_box.setObjectName("exportOptionsGroupBox")
        main_layout = QVBoxLayout()
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
        self.use_last_options_checkbox = QCheckBox()
        self.use_last_options_checkbox.setObjectName("useLastOptionsCheckbox")
        main_layout.addWidget(self.use_last_options_checkbox)
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
        self._setup_texts()
        self.apply_settings()
        self._set_folder_path()
        self._setup_combobox()
        self._setup_completer()
        self._set_validators()
        self._apply_date_state()
        self._setup_date_edits()
        self._set_required_style()
        self._apply_export_action_state()

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            ErrorHandler.handle_error(
                f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.folder_dialog_title = ui_texts.get(
            "folderDialogTitle", "Select Export Folder"
        )
        type_items = ui_texts.get(f"{self.file_type_combobox.objectName()}Items", [])
        if not type_items:
            ErrorHandler.handle_error(
                f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.file_type_combobox.addItems(type_items)
        self.all_customers_text = ui_texts.get("allCustomersText", "All customers...")
        if UiTexts.set_ui_texts(self, widgets):
            self.default_name = ui_texts.get(
                f"{self.file_name_line_edit.objectName()}Text", "Export"
            )
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_combobox(self) -> None:
        self.customer_combobox.addItem(self.all_customers_text, None)
        for customer in DbCache.customers:
            name, address = self.completer_model.format_customer(customer)
            self.customer_combobox.addItem(
                f"{name} - {address}",
                customer.id,
            )

    def _setup_completer(self) -> None:
        completer = QCompleter()
        completer.setModel(self.completer_model)
        completer.setCompletionRole(Qt.ItemDataRole.UserRole + 10)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.customer_combobox.setCompleter(completer)

    def apply_settings(self) -> None:
        if not UiSettings.apply_settings(
            "export", EXPORT_TYPE_TRANSACTIONS, self.findChildren(QWidget)
        ):
            ErrorHandler.handle_error(
                f"Settings load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_settings_error = "CONFIG_LOAD_FAILED"
            return
        self._set_folder_path()
        if not self.file_name_line_edit.text().strip():
            today = QDate.currentDate()
            self.file_name_line_edit.setText(
                f"{self.default_name}_{today.year()}_{today.month()}_{today.day()}"
            )
        self.today_radio_button.setChecked(True)
        self.customer_combobox.setEditable(True)
        self.in_radio_button.setChecked(True)

    def _create_connection(self) -> None:
        date_radiobuttons = [
            self.today_radio_button,
            self.week_radio_button,
            self.month_radio_button,
            self.year_radio_button,
            self.custom_radio_button,
        ]
        self.branch_name_line_edit.textChanged.connect(self._on_text_or_value_changed)
        self.file_name_line_edit.textChanged.connect(self._on_text_or_value_changed)
        self.path_button.clicked.connect(self._select_export_folder)
        for radio_button in date_radiobuttons:
            radio_button.toggled.connect(self._apply_date_state)
            radio_button.toggled.connect(self._update_sheet_state)
        self.from_date_edit.dateChanged.connect(self._update_to_date_minimum)
        self.from_date_edit.dateChanged.connect(self._update_sheet_state)
        self.to_date_edit.dateChanged.connect(self._update_from_date_maximum)
        self.to_date_edit.dateChanged.connect(self._update_sheet_state)
        self.customer_combobox.currentIndexChanged.connect(
            self._on_customer_selection_changed
        )
        self.customer_combobox.lineEdit().textEdited.connect(
            self._on_customer_text_edited
        )
        self.export_button.clicked.connect(
            self.transactions_export_controller.start_export
        )

    def _set_validators(self) -> None:
        name_validator = QRegularExpressionValidator(
            QRegularExpression(r"[A-Za-zÀ-ž0-9_\- ]{1,30}")
        )
        self.branch_name_line_edit.setValidator(name_validator)
        self.file_name_line_edit.setValidator(name_validator)

    def _set_folder_path(self) -> None:
        if not self.path_line_edit.text().strip():
            self.current_path = Path(
                QStandardPaths.writableLocation(
                    QStandardPaths.StandardLocation.DocumentsLocation
                )
            )
        else:
            self.current_path = Path(self.path_line_edit.text().strip())
        self._set_elided_path(str(self.current_path))
        self.path_line_edit.setToolTip(str(self.current_path))
        self.path_line_edit.setToolTipDuration(3000)
        self.path_line_edit.setReadOnly(True)

    def _on_text_or_value_changed(self) -> None:
        self._apply_export_action_state()
        self._set_required_style()

    def _on_customer_selection_changed(self, index: int) -> None:
        self._apply_export_action_state()

    def _on_customer_text_edited(self, text: str) -> None:
        if not text:
            QTimer.singleShot(300, self._reset_customer_selection)
        self._apply_export_action_state()

    def _reset_customer_selection(self) -> None:
        if self.customer_combobox.currentText().strip():
            return
        self.customer_combobox.setCurrentIndex(0)
        self._apply_export_action_state()

    def _is_customer_selection_valid(self) -> bool:
        text = self.customer_combobox.currentText().strip()
        if text == self.all_customers_text:
            return self.customer_combobox.currentIndex() == 0
        index = self.customer_combobox.findText(
            text,
            Qt.MatchFlag.MatchExactly,
        )
        if index < 1:
            return False
        return (
            self.customer_combobox.itemData(index, Qt.ItemDataRole.UserRole) is not None
        )

    def _apply_date_state(self) -> None:
        if self.custom_radio_button.isChecked():
            self.from_date_edit.setEnabled(True)
            self.to_date_edit.setEnabled(True)
        else:
            self.from_date_edit.setEnabled(False)
            self.to_date_edit.setEnabled(False)

    def _update_sheet_state(self) -> None:
        if self.year_radio_button.isChecked():
            self.month_split_checkbox.setEnabled(True)
            self.month_split_checkbox.setChecked(True)
            return
        if (
            self.custom_radio_button.isChecked()
            and abs(
                self.from_date_edit.date().month() - self.to_date_edit.date().month()
            )
            > 0
        ):
            self.month_split_checkbox.setEnabled(True)
            self.month_split_checkbox.setChecked(True)
            return
        self.month_split_checkbox.setEnabled(False)
        self.month_split_checkbox.setChecked(False)

    def _apply_export_action_state(self) -> None:
        if (
            self.branch_name_line_edit.text().strip() != ""
            and self.file_name_line_edit.text().strip() != ""
            and self._is_customer_selection_valid()
        ):
            self.export_button.setEnabled(True)
        else:
            self.export_button.setEnabled(False)

    def _setup_date_edits(self) -> None:
        date_edits = [self.from_date_edit, self.to_date_edit]
        for date_edit in date_edits:
            calendar = date_edit.calendarWidget()
            if calendar:
                calendar.setMinimumWidth(250)
                calendar.setMinimumHeight(200)
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

    def _set_elided_path(self, path: str) -> None:
        metrics = QFontMetrics(self.path_line_edit.font())
        elided_path = metrics.elidedText(
            path, Qt.TextElideMode.ElideMiddle, self.path_line_edit.width()
        )
        self.path_line_edit.setText(elided_path)

    def _select_export_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, self.folder_dialog_title, str(self.current_path)
        )
        if folder:
            self.current_path = Path(folder)
            self._set_elided_path(str(self.current_path))
            self.path_line_edit.setToolTip(str(folder))

    def _get_export_path(self) -> Path:
        return self.current_path / self.file_name_line_edit.text().strip()

    def _get_date_interval(self) -> tuple[str, str]:
        date_map = {
            self.today_radio_button: "today",
            self.week_radio_button: "week",
            self.month_radio_button: "month",
            self.year_radio_button: "year",
        }
        for key, value in date_map.items():
            if key.isChecked():
                date_range = get_filter_range(value)
                if date_range is not None:
                    return date_range
        date_range = (
            self.from_date_edit.date().toString("yyyy-MM-dd 00:00:00"),
            self.to_date_edit.date().toString("yyyy-MM-dd 23:59:59"),
        )
        return date_range

    def _get_transfer_type(self) -> tuple[str | None, str | None]:
        transfer_map = {
            self.all_radio_button: (TRANSFER_IN, TRANSFER_OUT),
            self.in_radio_button: (TRANSFER_IN, None),
            self.out_radio_button: (None, TRANSFER_OUT),
        }
        for button, transfer_type in transfer_map.items():
            if button.isChecked():
                return transfer_type
        return TRANSFER_IN, None

    @staticmethod
    def _get_file_suffix(file_type: str) -> str:
        file_map = {
            "Excel": ".xlsx",
        }
        return file_map[file_type]

    def get_export_data(self) -> dict[str, Path | str | int | None | bool]:
        from_date, to_date = self._get_date_interval()
        return {
            "branchNameLineEdit": self.branch_name_line_edit.text().strip(),
            "pathLineEdit": str(self.current_path),
            "export_path": self._get_export_path(),
            "fileNameLineEdit": self.file_name_line_edit.text().strip(),
            "from_date": from_date,
            "to_date": to_date,
            "split_by_month": self.month_split_checkbox.isChecked(),
            "customer_id": self.customer_combobox.currentData(Qt.ItemDataRole.UserRole),
            "transfer_type": self._get_transfer_type(),
            "noActionRadioButton": self.no_action_radio_button.isChecked(),
            "openFolderRadioButton": self.open_folder_radio_button.isChecked(),
            "openFileRadioButton": self.open_file_radio_button.isChecked(),
            "useLastOptionsCheckbox": self.use_last_options_checkbox.isChecked(),
        }

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._set_elided_path(str(self.current_path))
