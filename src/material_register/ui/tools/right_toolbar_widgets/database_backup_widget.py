import os
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from material_register.controllers.tools_controllers.database_backup_controller import (
    DatabaseBackupController,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.tools.right_toolbar_widgets.database_backup_widgets.database_backup_tree_widget import (
    DatabaseBackupTreeWidget,
)

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widget import RightToolbarWidget


class DatabaseBackupWidget(QWidget):
    def __init__(self, right_toolbar_widget: "RightToolbarWidget") -> None:
        super().__init__(right_toolbar_widget)
        self.right_toolbar_widget = right_toolbar_widget
        self.database_backup_controller = DatabaseBackupController(self)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()
        self.backup_path = None

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(5)
        self.info_group = self._create_info_group()
        self.backup_group = self._create_backup_group()
        scroll_layout.addWidget(self.info_group)
        scroll_layout.addWidget(self.backup_group, 1)
        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self.setup_info_group()
        self.setup_backup_tree()
        self._setup_widgets()

    def _create_info_group(self) -> QGroupBox:
        info_group_box = QGroupBox()
        info_group_box.setObjectName("infoGroupBox")
        info_layout = QFormLayout()
        info_layout.setFieldGrowthPolicy(
            QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self.database_name_label = QLabel()
        self.database_name_label.setObjectName("databaseNameLabel")
        self.database_name_value = QLabel()
        self.database_name_value.setObjectName("databaseNameValue")
        self.database_name_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.database_size_label = QLabel()
        self.database_size_label.setObjectName("databaseSizeLabel")
        self.database_size_value = QLabel()
        self.database_size_value.setObjectName("databaseSizeValue")
        self.database_size_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.database_last_modified_label = QLabel()
        self.database_last_modified_label.setObjectName("databaseLastModifiedLabel")
        self.database_last_modified_value = QLabel()
        self.database_last_modified_value.setObjectName("databaseLastModifiedValue")
        self.database_last_modified_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.database_last_backup_label = QLabel()
        self.database_last_backup_label.setObjectName("databaseLastBackupLabel")
        self.database_last_backup_value = QLabel()
        self.database_last_backup_value.setObjectName("databaseLastBackupValue")
        self.database_last_backup_value.setAlignment(Qt.AlignmentFlag.AlignRight)
        info_layout.addRow(self.database_name_label, self.database_name_value)
        info_layout.addRow(self.database_size_label, self.database_size_value)
        info_layout.addRow(
            self.database_last_modified_label, self.database_last_modified_value
        )
        info_layout.addRow(
            self.database_last_backup_label, self.database_last_backup_value
        )
        info_group_box.setLayout(info_layout)
        return info_group_box

    def _create_backup_group(self) -> QGroupBox:
        backup_group_box = QGroupBox()
        backup_group_box.setObjectName("backupGroupBox")
        backup_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        self.custom_backup_button = QPushButton()
        self.custom_backup_button.setObjectName("customBackupButton")
        self.no_backup_label = QLabel()
        self.no_backup_label.setObjectName("noBackupLabel")
        self.no_backup_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.no_backup_label.setFont(font)
        self.backup_tree_widget = DatabaseBackupTreeWidget(self)
        self.backup_tree_widget.setObjectName("backupTreeWidget")
        selected_layout = QHBoxLayout()
        self.selected_backup_label = QLabel()
        self.selected_backup_label.setObjectName("selectedBackupLabel")
        self.selected_path_label = QLabel()
        self.selected_path_label.setObjectName("selectedPathLabel")
        actions_group_box = QGroupBox()
        actions_layout = QHBoxLayout()
        self.custom_restore_button = QPushButton()
        self.custom_restore_button.setObjectName("customRestoreButton")
        self.restore_backup_button = QPushButton()
        self.restore_backup_button.setObjectName("restoreBackupButton")
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.custom_backup_button)
        selected_layout.addWidget(self.selected_backup_label)
        selected_layout.addWidget(self.selected_path_label, 1)
        actions_layout.addWidget(self.custom_restore_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.restore_backup_button)
        actions_group_box.setLayout(actions_layout)
        backup_layout.addLayout(buttons_layout)
        backup_layout.addWidget(self.no_backup_label, 1)
        backup_layout.addWidget(self.backup_tree_widget, 1)
        backup_layout.addLayout(selected_layout)
        backup_layout.addWidget(actions_group_box)
        backup_group_box.setLayout(backup_layout)
        return backup_group_box

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.selected_path_text = ui_texts.get("selectedPathLabelText", "Select a backup")
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_widgets(self) -> None:
        self.restore_backup_button.setDisabled(True)

    def _create_connection(self) -> None:
        self.backup_tree_widget.itemSelectionChanged.connect(self._update_backup_path)
        self.backup_tree_widget.itemSelectionChanged.connect(self._update_backup_button_state)

    def setup_info_group(self) -> None:
        name, size, modified, last_backup = (
            self.database_backup_controller.setup_database_info_group()
        )
        self.database_name_value.setText(name)
        self.database_size_value.setText(str(size))
        self.database_last_modified_value.setText(str(modified))
        self.database_last_backup_value.setText(str(last_backup))

    def setup_backup_tree(self) -> None:
        backup_map = self.database_backup_controller.get_backup_map()
        is_backup = bool(backup_map)
        self.backup_tree_widget.setVisible(is_backup)
        self.no_backup_label.setVisible(not is_backup)
        if is_backup:
            self.backup_tree_widget.load_tree_widget(backup_map)

    def _update_backup_path(self) -> None:
        backup_path = self.backup_tree_widget.get_selected_data()
        if backup_path is None:
            self.backup_path = None
            self.selected_path_label.setText(self.selected_path_text)
            return
        self.backup_path = backup_path
        displayed_name = f"...{os.sep}{str(self.backup_path.relative_to(self.database_backup_controller.backup_path))}"
        self.selected_path_label.setText(displayed_name)

    def _update_backup_button_state(self) -> None:
        self.restore_backup_button.setDisabled(self.backup_path is None)