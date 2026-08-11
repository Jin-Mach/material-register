from typing import TYPE_CHECKING

from PySide6.QtCore import QRegularExpression, QStandardPaths, Qt
from PySide6.QtGui import QFontMetrics, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QCheckBox,
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

from material_register.controllers.settings_controller import SettingsController
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_settings import UiSettings
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.settings.settings_widget import SettingsWidget


class PeriodExportSettings(QWidget):
    WIDTH = 400
    SPACING = 20

    def __init__(self, settings_widget: "SettingsWidget") -> None:
        super().__init__(settings_widget)
        self.settings_widget = settings_widget
        self.settings_controller = SettingsController(self)
        self.current_path = ""
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        group_widget = QWidget()
        group_layout = QVBoxLayout()
        group_layout.setSpacing(self.SPACING)
        branch_group = self._create_branch_group()
        path_name_group = self._create_path_name_group()
        export_options_group = self._create_export_options_group()
        other_settings_group = self._create_other_settings_group()
        group_layout.addWidget(branch_group)
        group_layout.addWidget(path_name_group)
        group_layout.addWidget(export_options_group)
        group_layout.addWidget(other_settings_group)
        actions_group = self._create_actions_group()
        group_widget.setLayout(group_layout)
        scroll_area.setWidget(group_widget)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(actions_group)
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
        form_layout.addRow(self.path_label, path_layout)
        form_layout.addRow(self.file_name_label, name_layout)
        main_layout.addLayout(form_layout)
        self.path_name_group_box.setLayout(main_layout)
        return self.path_name_group_box

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
        self.save_last_opening_balance_checkbox.setObjectName(
            "saveLastOpeningBalanceCheckbox"
        )
        main_layout.addWidget(self.use_last_options_checkbox)
        main_layout.addWidget(self.save_last_opening_balance_checkbox)
        self.other_settings_group_box.setLayout(main_layout)
        return self.other_settings_group_box

    def _create_actions_group(self) -> QGroupBox:
        self.actions_group_box = QGroupBox()
        self.actions_group_box.setObjectName("actionsGroupBox")
        main_layout = QHBoxLayout()
        main_layout.setSpacing(self.SPACING)
        self.restore_button = QPushButton()
        self.restore_button.setObjectName("restoreButton")
        self.save_button = QPushButton()
        self.save_button.setObjectName("saveButton")
        main_layout.addStretch()
        main_layout.addWidget(self.restore_button)
        main_layout.addWidget(self.save_button)
        self.actions_group_box.setLayout(main_layout)
        return self.actions_group_box

    def _setup_ui(self) -> None:
        self._setup_texts()
        self.apply_settings()
        self._set_folder_path()
        self._set_validators()

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
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def apply_settings(self) -> None:
        if not UiSettings.set_ui_settings("export", self.findChildren(QWidget)):
            ErrorHandler.handle_error(
                f"Settings load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_settings_error = "CONFIG_LOAD_FAILED"
            return

    def _create_connection(self) -> None:
        self.path_button.clicked.connect(self._select_export_path)
        self.restore_button.clicked.connect(self.settings_controller.restore_settings)
        self.save_button.clicked.connect(self.settings_controller.update_settings)

    def _set_validators(self) -> None:
        name_validator = QRegularExpressionValidator(
            QRegularExpression(r"[A-Za-zÀ-ž0-9_\- ]{1,30}")
        )
        self.branch_name_line_edit.setValidator(name_validator)
        self.file_name_line_edit.setValidator(name_validator)

    def _set_folder_path(self) -> None:
        if not self.path_line_edit.text().strip():
            self.current_path = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DocumentsLocation
            )
        else:
            self.current_path = self.path_line_edit.text().strip()
        self._set_elided_path(self.current_path)
        self.path_line_edit.setToolTip(self.current_path)
        self.path_line_edit.setToolTipDuration(3000)
        self.path_line_edit.setReadOnly(True)

    def _set_elided_path(self, path: str) -> None:
        metrics = QFontMetrics(self.path_line_edit.font())
        elided_path = metrics.elidedText(
            path, Qt.TextElideMode.ElideMiddle, self.path_line_edit.width()
        )
        self.path_line_edit.setText(elided_path)

    def _select_export_path(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self, self.folder_dialog_title, self.current_path
        )
        if folder:
            self.current_path = folder
            self._set_elided_path(self.current_path)
            self.path_line_edit.setToolTip(self.current_path)

    def get_export_settings_data(self):
        return {
            self.branch_name_line_edit.objectName(): self.branch_name_line_edit.text().strip(),
            self.path_line_edit.objectName(): self.current_path,
            self.file_name_line_edit.objectName(): self.file_name_line_edit.text().strip(),
            self.no_action_radio_button.objectName(): self.no_action_radio_button.isChecked(),
            self.open_folder_radio_button.objectName(): self.open_folder_radio_button.isChecked(),
            self.open_file_radio_button.objectName(): self.open_file_radio_button.isChecked(),
            self.use_last_options_checkbox.objectName(): self.use_last_options_checkbox.isChecked(),
            self.save_last_opening_balance_checkbox.objectName(): self.save_last_opening_balance_checkbox.isChecked(),
        }
