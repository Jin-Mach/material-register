from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTabWidget, QVBoxLayout, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.export.export_widgets.summary_export_widget import (
    SummaryExportWidget,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class ExportWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.stacked_widget = stacked_widget
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.export_tab_widget = QTabWidget()
        main_layout.addWidget(self.export_tab_widget)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_tabs()

    def _setup_texts(self) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.summary_tab_title = ui_texts.get("summaryTabTitle", "Records")
        if ui_texts:
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"

    def _setup_tabs(self) -> None:
        self.summary_export_widget = SummaryExportWidget(self)
        self.export_tab_widget.addTab(
            self.summary_export_widget, self.summary_tab_title
        )
