from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit

from material_register.domain.category_dataclass import Category

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.catalog_details_widget import CatalogDetailsWidget


class CategoryDetailWidget(QWidget):
    def __init__(self, catalog_detail_widget: "CatalogDetailsWidget") -> None:
        super().__init__(catalog_detail_widget)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.category_name_label = QLabel()
        self.category_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.category_name_label.setFont(font)
        self.category_notes_edit = QTextEdit()
        self.category_notes_edit.setReadOnly(True)
        main_layout.addWidget(self.category_name_label)
        main_layout.addWidget(self.category_notes_edit)
        return main_layout

    def set_category_texts(self, category: Category) -> None:
        self.category_name_label.setText(category.name)
        self.category_notes_edit.setText(category.notes or "")