from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout

from material_register.ui.catalog.catalog_widgets.category_detail_widget import CategoryDetailWidget

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogDetailsWidget(QWidget):
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        super().__init__(catalog_widget)
        self.catalog_widget = catalog_widget
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.category_detail_widget = CategoryDetailWidget(self)
        button_layout = QHBoxLayout()
        self.add_commodity_button = QPushButton("Add commodity")
        button_layout.addStretch()
        button_layout.addWidget(self.add_commodity_button)
        main_layout.addWidget(self.category_detail_widget)
        main_layout.addLayout(button_layout)
        return main_layout

    def _setup_ui(self) -> None:
        self._update_state()

    def _create_connection(self) -> None:
        self.catalog_widget.tree_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.add_commodity_button.clicked.connect(self.catalog_widget.catalog_controller.add_commodity)

    def _update_state(self) -> None:
        self.add_commodity_button.setEnabled(self._is_selection())

    def _on_selection_changed(self) -> None:
        self._update_state()

    def _is_selection(self) -> bool:
        return self.catalog_widget.tree_widget.has_selection()