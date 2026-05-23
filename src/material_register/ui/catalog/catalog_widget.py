from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel

from material_register.controllers.catalog.catalog_controller import CatalogController
from material_register.ui.catalog.catalog_widgets.catalog_details_widget import CatalogDetailsWidget
from material_register.ui.catalog.catalog_widgets.catalog_tree_widget import CatalogTreeWidget

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class CatalogWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.catalog_controller = CatalogController(self)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        self.add_category_button = QPushButton("Add Category")
        self.add_category_button.setObjectName("addCategoryButton")
        self.catalog_title_label = QLabel("Catalog Title")
        self.catalog_title_label.setObjectName("catalogTitleLabel")
        self.catalog_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.catalog_title_label.setFont(font)
        bottom_layout = QHBoxLayout()
        self.tree_widget = CatalogTreeWidget(self)
        self.details_widget = CatalogDetailsWidget(self, self.catalog_controller)
        top_layout.addWidget(self.add_category_button)
        top_layout.addStretch()
        top_layout.addWidget(self.catalog_title_label)
        top_layout.addStretch()
        bottom_layout.addWidget(self.tree_widget, 1)
        bottom_layout.addWidget(self.details_widget, 3)
        main_layout.addLayout(top_layout)
        main_layout.addLayout(bottom_layout)
        return main_layout

    def _setup_ui(self) -> None:
        self._reload_data()

    def _create_connection(self) -> None:
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.add_category_button.clicked.connect(self.catalog_controller.add_category)
        self.details_widget.category_with_commodities_widget.category_detail_widget.update_category_button.clicked.connect(
            self.catalog_controller.update_category)
        self.details_widget.category_with_commodities_widget.category_detail_widget.add_commodity_button.clicked.connect(
            self.catalog_controller.add_commodity)

    def _reload_data(self) -> None:
        self.catalog_controller.reload_catalog_tree()

    def _on_selection_changed(self) -> None:
        self.catalog_controller.setup_details_widget()