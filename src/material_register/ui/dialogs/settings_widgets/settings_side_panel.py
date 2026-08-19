from typing import TYPE_CHECKING

from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

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
        self.export_button = QPushButton()
        self.export_button.setObjectName("exportButton")
        main_layout.addWidget(self.export_button)
        main_layout.addStretch()
        return main_layout

    def _setup_texts(self) -> None:
        widgets = [
            self.export_button,
        ]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)