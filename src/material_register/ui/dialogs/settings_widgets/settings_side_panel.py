from typing import TYPE_CHECKING

from PySide6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class SettingsSidePanel(QWidget):
    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        super().__init__(settings_dialog)
        self.setLayout(self._create_ui())
        self._setup_texts()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        group_box = QGroupBox()
        group_box.setObjectName("settingsSidePanelGroupBox")
        group_layout = QVBoxLayout()
        group_layout.setSpacing(5)
        self.export_button = QPushButton()
        self.export_button.setObjectName("exportButton")
        self.tools_button = QPushButton()
        self.tools_button.setObjectName("toolsButton")
        group_layout.addWidget(self.export_button)
        group_layout.addWidget(self.tools_button)
        group_layout.addStretch()
        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)
        return main_layout

    def _setup_texts(self) -> None:
        widgets = [
            self.export_button,
            self.tools_button,
        ]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)
