from typing import TYPE_CHECKING

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QScrollArea, QHBoxLayout, QLabel, QFormLayout,
                               QLineEdit,
                               QPushButton, QSizePolicy, QRadioButton, QCheckBox)

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.settings.settings_widget import SettingsWidget


class ExportSettings(QWidget):
    WIDTH = 400
    SPACING = 20

    def __init__(self, settings_widget: "SettingsWidget") -> None:
        super().__init__(settings_widget)
        self.setLayout(self._create_ui())
        self._setup_ui()

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
        other_settings_group = self._create_other_settings()
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

    def _create_other_settings(self) -> QGroupBox:
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

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return