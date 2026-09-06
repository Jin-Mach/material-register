from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from material_register.controllers.tools_controllers.database_backup_controller import (
    DatabaseBackupController,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widget import RightToolbarWidget


class DatabaseBackupWidget(QWidget):
    def __init__(self, right_toolbar_widget: "RightToolbarWidget") -> None:
        super().__init__(right_toolbar_widget)
        self.right_toolbar_widget = right_toolbar_widget
        self.database_backup_controller = DatabaseBackupController(self)
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        self.info_group = self._create_info_group()

        scroll_layout.addWidget(self.info_group)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_info_group()

    def _create_info_group(self) -> QGroupBox:
        info_group_box = QGroupBox()
        info_group_box.setObjectName("infoGroupBox")
        info_layout = QFormLayout()
        self.database_name_label = QLabel()
        self.database_name_label.setObjectName("databaseNameLabel")
        self.database_name_value = QLabel()
        self.database_name_value.setObjectName("databaseNameValue")
        self.database_size_label = QLabel()
        self.database_size_label.setObjectName("databaseSizeLabel")
        self.database_size_value = QLabel()
        self.database_size_value.setObjectName("databaseSizeValue")
        self.database_last_modified_label = QLabel()
        self.database_last_modified_label.setObjectName("databaseLastModifiedLabel")
        self.database_last_modified_value = QLabel()
        self.database_last_modified_value.setObjectName("databaseLastModifiedValue")
        info_layout.addRow(self.database_name_label, self.database_name_value)
        info_layout.addRow(self.database_size_label, self.database_size_value)
        info_layout.addRow(
            self.database_last_modified_label, self.database_last_modified_value
        )
        info_group_box.setLayout(info_layout)
        return info_group_box

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_info_group(self) -> None:
        name, size, modified = (
            self.database_backup_controller.setup_database_info_group()
        )
        self.database_name_value.setText(name)
        self.database_size_value.setText(str(size))
        self.database_last_modified_value.setText(str(modified))
