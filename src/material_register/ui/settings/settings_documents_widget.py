from typing import TYPE_CHECKING

from PySide6.QtCore import QStandardPaths, Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtPrintSupport import QPrinterInfo
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from material_register.controllers.settings_controllers.documents_settings_controller import (
    DocumentsSettingsController,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    UI_MARGINS_5,
    UI_SPACING,
)
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class SettingsDocumentsWidget(QWidget):
    WIDTH = 400

    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        super().__init__(settings_dialog)
        self.settings_dialog = settings_dialog
        self.documents_settings_controller = DocumentsSettingsController(
            self.settings_dialog
        )
        self.printer_name = ""
        self.save_current_path = ""
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        group_widget = QWidget()
        group_layout = QVBoxLayout()
        group_layout.setSpacing(UI_SPACING)
        group_layout.setContentsMargins(*UI_MARGINS_5)
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
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        form_layout = QFormLayout()
        form_layout.setSpacing(UI_SPACING)
        form_layout.setContentsMargins(*UI_MARGINS_5)
        self.printer_name_label = QLabel()
        self.printer_name_label.setObjectName("printerNameLabel")
        self.printer_name_line_edit = QLineEdit()
        self.printer_name_line_edit.setObjectName("printerNameLineEdit")
        self.printer_name_line_edit.setMinimumWidth(self.WIDTH)
        self.printer_name_line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        self.printer_name_line_edit.setReadOnly(True)
        self.printer_name_button = QPushButton()
        self.printer_name_button.setObjectName("printerNameButton")
        path_layout = QHBoxLayout()
        path_layout.setSpacing(UI_SPACING)
        path_layout.setContentsMargins(*UI_MARGINS_5)
        path_layout.addWidget(self.printer_name_line_edit)
        path_layout.addWidget(self.printer_name_button)
        form_layout.addRow(self.printer_name_label, path_layout)
        main_layout.addLayout(form_layout)
        self.print_group_box.setLayout(main_layout)
        return self.print_group_box

    def _create_save_group(self) -> QGroupBox:
        self.save_group_box = QGroupBox()
        self.save_group_box.setObjectName("saveGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        form_layout = QFormLayout()
        form_layout.setSpacing(UI_SPACING)
        form_layout.setContentsMargins(*UI_MARGINS_5)
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
        path_layout.setSpacing(UI_SPACING)
        path_layout.setContentsMargins(*UI_MARGINS_5)
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
        main_layout.setSpacing(UI_SPACING * 2)
        main_layout.setContentsMargins(*UI_MARGINS_5)
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
        self.apply_settings()
        self.set_folder_path()
        self._create_connection()

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.printer_dialog_title = ui_texts.get("printerDialogTitle", "Select Printer")
        self.folder_dialog_title = ui_texts.get("folderDialogTitle", "Select Folder")
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def apply_settings(self) -> None:
        user_settings = self.documents_settings_controller.settings.get("user", {})
        self.printer_name = user_settings.get("printerNameLineEdit", "")
        self.save_current_path = user_settings.get("savePathLineEdit", "")

    def set_folder_path(self) -> None:
        documents_path = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation
        )
        if not self.save_current_path:
            self.save_current_path = documents_path
        self.printer_name_line_edit.setText(self.printer_name)
        self._set_elided_path(self.save_path_line_edit, self.save_current_path)
        self.printer_name_line_edit.setToolTip(self.printer_name)
        self.save_path_line_edit.setToolTip(self.save_current_path)
        self.printer_name_line_edit.setToolTipDuration(3000)
        self.save_path_line_edit.setToolTipDuration(3000)

    def _create_connection(self) -> None:
        self.printer_name_button.clicked.connect(self.select_printer)
        self.save_path_button.clicked.connect(self.select_save_path)
        self.restore_button.clicked.connect(
            lambda: self.documents_settings_controller.restore_settings(self)
        )
        self.save_button.clicked.connect(
            lambda: self.documents_settings_controller.update_settings(self)
        )

    def select_printer(self) -> None:
        printers = QPrinterInfo.availablePrinters()
        if not printers:
            MessageBoxes.show_error(self, "NO_PRINTERS")
            return
        printer_names = []
        for printer in printers:
            printer_names.append(printer.printerName())
        current_index = (
            printer_names.index(self.printer_name)
            if self.printer_name in printer_names
            else 0
        )
        printer_name, accepted = QInputDialog.getItem(
            self,
            self.printer_dialog_title,
            self.printer_name_label.text(),
            printer_names,
            current_index,
            False,
        )
        if not accepted:
            return
        self.printer_name = printer_name
        self.printer_name_line_edit.setText(self.printer_name)
        self.printer_name_line_edit.setToolTip(self.printer_name)

    def select_save_path(self) -> None:
        path = QFileDialog.getExistingDirectory(
            self,
            self.folder_dialog_title,
            self.save_current_path,
        )
        if not path:
            return
        self.save_current_path = path
        self._set_elided_path(self.save_path_line_edit, self.save_current_path)
        self.save_path_line_edit.setToolTip(self.save_current_path)

    @staticmethod
    def _set_elided_path(line_edit: QLineEdit, path: str) -> None:
        metrics = QFontMetrics(line_edit.font())
        elided_path = metrics.elidedText(
            path, Qt.TextElideMode.ElideMiddle, line_edit.width()
        )
        line_edit.setText(elided_path)

    def get_documents_settings_data(self) -> dict[str, str]:
        return {
            "printerNameLineEdit": self.printer_name,
            "savePathLineEdit": self.save_current_path,
        }
