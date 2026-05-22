from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.catalog_details_widget import CatalogDetailsWidget


class CatalogDefaultWidget(QWidget):
    def __init__(self, catalog_details_widget: "CatalogDetailsWidget") -> None:
        super().__init__(catalog_details_widget)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.title_label = QLabel("Material register")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.subtitle_label = QLabel("Category and commodities\n(select for details)")
        self.subtitle_label.setObjectName("subtitleLabel")
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addStretch()
        main_layout.addWidget(self.title_label)
        main_layout.addWidget(self.subtitle_label)
        main_layout.addStretch()
        return main_layout

    def set_ui_data(self) -> None:
        pass