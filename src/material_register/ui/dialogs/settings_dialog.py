from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QVBoxLayout

from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.settings_widgets.settings_side_panel import (
    SettingsSidePanel,
)
from material_register.ui.dialogs.settings_widgets.settings_stacked_widget import (
    SettingsStackedWidget,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class SettingsDialog(QDialog):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.setMinimumSize(900, 600)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        widgets_layout = QHBoxLayout()
        settings_side_panel = SettingsSidePanel(self)
        settings_stacked_widget = SettingsStackedWidget(self)
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        self.close_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.close_button.setObjectName("closeButton")
        widgets_layout.addWidget(settings_side_panel)
        widgets_layout.addWidget(settings_stacked_widget)
        main_layout.addLayout(widgets_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        if UiTexts.set_ui_texts(self, [self.close_button]):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, []):
            return

    def _create_connection(self):
        self.close_button.clicked.connect(self.close)