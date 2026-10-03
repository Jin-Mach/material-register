from typing import TYPE_CHECKING

from PySide6.QtCore import QMargins, Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from material_register.controllers.catalog_controller import CatalogController
from material_register.services.error_handler import ErrorHandler
from material_register.ui.catalog.catalog_widgets.catalog_details_widget import (
    CatalogDetailsWidget,
)
from material_register.ui.catalog.catalog_widgets.catalog_tree_widget import (
    CatalogTreeWidget,
)
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class CatalogWidget(QWidget):
    SPACING = 5
    MARGINS = QMargins(5, 5, 5, 5)

    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.catalog_controller = CatalogController(self)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        main_layout.setContentsMargins(self.MARGINS)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(self.SPACING)
        content_layout.setContentsMargins(self.MARGINS)
        self.add_category_button = QPushButton()
        self.add_category_button.setObjectName("addCategoryButton")
        self.update_commodities_price = QPushButton()
        self.update_commodities_price.setObjectName("updateCommoditiesPrice")
        self.catalog_title_label = QLabel()
        self.catalog_title_label.setObjectName("catalogTitleLabel")
        self.catalog_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.catalog_title_label.setFont(font)
        self.tree_widget = CatalogTreeWidget(self)
        self.details_widget = CatalogDetailsWidget(self, self.catalog_controller)
        self.catalog_group_box = QGroupBox()
        catalog_group_layout = QVBoxLayout()
        catalog_group_layout.setSpacing(self.SPACING)
        catalog_group_layout.setContentsMargins(self.MARGINS)
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(self.SPACING * 2)
        actions_layout.setContentsMargins(self.MARGINS)
        actions_layout.addWidget(self.add_category_button)
        actions_layout.addWidget(self.update_commodities_price)
        actions_layout.addStretch()
        catalog_group_layout.addLayout(actions_layout)
        catalog_group_layout.addWidget(self.tree_widget, 1)
        self.catalog_group_box.setLayout(catalog_group_layout)
        self.details_group_box = QGroupBox()
        details_group_layout = QVBoxLayout()
        details_group_layout.setSpacing(self.SPACING)
        details_group_layout.setContentsMargins(self.MARGINS)
        details_group_layout.addWidget(self.catalog_title_label)
        details_group_layout.addWidget(self.details_widget, 1)
        self.details_group_box.setLayout(details_group_layout)
        content_layout.addWidget(self.catalog_group_box, 0)
        content_layout.addWidget(self.details_group_box, 1)
        main_layout.addLayout(content_layout)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._reload_data()

    def _setup_texts(self) -> None:
        widgets = [
            self.add_category_button,
            self.update_commodities_price,
            self.catalog_title_label,
            self.details_widget,
        ]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _create_connection(self) -> None:
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.add_category_button.clicked.connect(self.catalog_controller.add_category)
        self.update_commodities_price.clicked.connect(
            self.catalog_controller.update_commodities_price
        )
        self.details_widget.category_with_commodities_widget.category_detail_widget.update_category_button.clicked.connect(
            self.catalog_controller.update_category
        )
        self.details_widget.category_with_commodities_widget.category_detail_widget.add_commodity_button.clicked.connect(
            self.catalog_controller.add_commodity
        )

    def _reload_data(self) -> None:
        self.catalog_controller.reload_catalog_tree()

    def _on_selection_changed(self) -> None:
        self.catalog_controller.setup_details_widget()
