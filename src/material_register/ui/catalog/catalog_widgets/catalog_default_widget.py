from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.catalog_details_widget import (
        CatalogDetailsWidget,
    )


class CatalogDefaultWidget(QWidget):
    def __init__(self, catalog_details_widget: "CatalogDetailsWidget") -> None:
        super().__init__(catalog_details_widget)
        self.setLayout(self._create_ui())
        self._setup_texts()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.title_label = QLabel()
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addStretch()
        return main_layout

    def _setup_texts(self) -> None:
        widgets = [self.title_label, self.subtitle_label]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return