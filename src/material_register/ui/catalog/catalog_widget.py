from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QToolButton

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

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        tree_layout = QVBoxLayout()
        actions_layout = QHBoxLayout()
        self.add_category_action = QToolButton()
        self.add_category_action.setObjectName("addCategoryAction")
        self.add_category_action.setText("+")
        self.update_category_action = QToolButton()
        self.update_category_action.setObjectName("updateCategoryAction")
        self.update_category_action.setText("/")
        self.tree_widget = CatalogTreeWidget(self)
        self.details_widget = CatalogDetailsWidget(self)
        actions_layout.addWidget(self.add_category_action)
        actions_layout.addWidget(self.update_category_action)
        actions_layout.addStretch()
        tree_layout.addLayout(actions_layout)
        tree_layout.addWidget(self.tree_widget)
        main_layout.addLayout(tree_layout, 1)
        main_layout.addWidget(self.details_widget, 1)
        return main_layout

    def _setup_ui(self) -> None:
        self.update_category_action.setEnabled(False)
        self._reload_data()

    def _create_connection(self) -> None:
        self.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.add_category_action.clicked.connect(self.catalog_controller.add_category)
        self.update_category_action.clicked.connect(self.catalog_controller.update_category)

    def _reload_data(self) -> None:
        self.catalog_controller.reload_catalog_tree()

    def _on_selection_changed(self) -> None:
        self.update_category_action.setEnabled(self.tree_widget.has_selection())
        self.setup_category_details_widget()

    def setup_category_details_widget(self) -> None:
        category = self.tree_widget.get_selected_category()
        if category:
            self.details_widget.category_detail_widget.set_category_texts(category)