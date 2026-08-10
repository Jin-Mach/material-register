from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.settings.settings_widgets.period_export_settings import PeriodExportSettings
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class SettingsWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.stacked_widget = stacked_widget
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
        if not ui_texts:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self._export_tab_title = ui_texts.get("periodExportTabTitle", "Records")

    def _setup_tabs(self) -> None:
        self.period_export_settings = PeriodExportSettings(self)
        self.settings_tab_widget.addTab(self.period_export_settings, self._export_tab_title)