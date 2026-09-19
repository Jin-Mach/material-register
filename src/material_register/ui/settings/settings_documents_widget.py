from typing import TYPE_CHECKING

from PySide6.QtCore import QStandardPaths, Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class SettingsDocumentsWidget(QWidget):
    WIDTH = 400
    SPACING = 10

    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        super().__init__(settings_dialog)
        self.settings_dialog = settings_dialog
        self.print_current_path = ""
        self.save_current_path = ""
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        group_widget = QWidget()
        group_layout = QVBoxLayout()
        group_layout.addWidget(self._create_print_group())
        group_layout.addWidget(self._create_save_group())
        group_layout.addStretch()
        group_widget.setLayout(group_layout)
        scroll_area.setWidget(group_widget)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(self._create_actions_group())
        return main_layout

    def _create_print_group(self) -> QGroupBox:
        self.print_group_box = QGroupBox()
        self.print_group_box.setObjectName("printGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        form_layout = QFormLayout()
        self.print_path_label = QLabel()
        self.print_path_label.setObjectName("printPathLabel")
        self.print_path_line_edit = QLineEdit()
        self.print_path_line_edit.setObjectName("printPathLineEdit")
        self.print_path_line_edit.setMinimumWidth(self.WIDTH)
        self.print_path_line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.print_path_line_edit.setReadOnly(True)
        self.print_path_button = QPushButton()
        self.print_path_button.setObjectName("printPathButton")
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.print_path_line_edit)
        path_layout.addWidget(self.print_path_button)
        form_layout.addRow(self.print_path_label, path_layout)
        main_layout.addLayout(form_layout)
        self.print_group_box.setLayout(main_layout)
        return self.print_group_box

    def _create_save_group(self) -> QGroupBox:
        self.save_group_box = QGroupBox()
        self.save_group_box.setObjectName("saveGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        form_layout = QFormLayout()
        self.save_path_label = QLabel()
        self.save_path_label.setObjectName("savePathLabel")
        self.save_path_line_edit = QLineEdit()
        self.save_path_line_edit.setObjectName("savePathLineEdit")
        self.save_path_line_edit.setMinimumWidth(self.WIDTH)
        self.save_path_line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.save_path_line_edit.setReadOnly(True)
        self.save_path_button = QPushButton()
        self.save_path_button.setObjectName("savePathButton")
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.save_path_line_edit)
        path_layout.addWidget(self.save_path_button)
        form_layout.addRow(self.save_path_label, path_layout)
        main_layout.addLayout(form_layout)
        self.save_group_box.setLayout(main_layout)
        return self.save_group_box

    def _create_actions_group(self) -> QGroupBox:
        self.actions_group_box = QGroupBox()
        self.actions_group_box.setObjectName("actionsGroupBox")
        main_layout = QHBoxLayout()
        main_layout.setSpacing(self.SPACING)
        self.settings_info_label = QLabel()
        self.settings_info_label.setObjectName("settingsInfoLabel")
        self.restore_button = QPushButton()
        self.restore_button.setObjectName("restoreButton")
        self.save_button = QPushButton()
        self.save_button.setObjectName("saveButton")
        main_layout.addWidget(self.settings_info_label)
        main_layout.addStretch()
        main_layout.addWidget(self.restore_button)
        main_layout.addWidget(self.save_button)
        self.actions_group_box.setLayout(main_layout)
        return self.actions_group_box

    def _setup_ui(self) -> None:
        self._setup_texts()
        self.set_folder_path()

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def set_folder_path(self) -> None:
        documents_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        self.print_current_path = documents_path
        self.save_current_path = documents_path
        SettingsDocumentsWidget._set_elided_path(
            self.print_path_line_edit, self.print_current_path
        )
        SettingsDocumentsWidget._set_elided_path(
            self.save_path_line_edit, self.save_current_path
        )
        self.print_path_line_edit.setToolTip(self.print_current_path)
        self.save_path_line_edit.setToolTip(self.save_current_path)
        self.print_path_line_edit.setToolTipDuration(3000)
        self.save_path_line_edit.setToolTipDuration(3000)

    @staticmethod
    def _set_elided_path(line_edit: QLineEdit, path: str) -> None:
        metrics = QFontMetrics(line_edit.font())
        elided_path = metrics.elidedText(
            path, Qt.TextElideMode.ElideMiddle, line_edit.width()
        )
        line_edit.setText(elided_path)
