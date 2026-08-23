from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from material_register.controllers.export_settings_controller import (
    ExportSettingsController,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.settings.settings_widgets.summary_export_settings import (
    SummaryExportSettings,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class SettingsExportWidget(QWidget):
    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        super().__init__(settings_dialog)
        self.settings_dialog = settings_dialog
        self.export_settings_controller = ExportSettingsController(settings_dialog)
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.settings_tab_widget = QTabWidget()
        main_layout.addWidget(self.settings_tab_widget)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_tabs()

    def _setup_texts(self) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self._export_tab_title = ui_texts.get("summaryExportTabTitle", "Records")
        if ui_texts:
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"

    def _setup_tabs(self) -> None:
        self.summary_export_settings = SummaryExportSettings(
            self.export_settings_controller, self
        )
        self.settings_tab_widget.addTab(
            self.summary_export_settings, self._export_tab_title
        )
