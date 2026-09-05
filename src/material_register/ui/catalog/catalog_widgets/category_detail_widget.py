from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from material_register.domain.category_dataclass import Category
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widgets.category_with_commodities_widget import (
        CategoryWithCommoditiesWidget,
    )


class CategoryDetailWidget(QWidget):
    def __init__(
        self, category_with_commodities_widget: "CategoryWithCommoditiesWidget"
    ) -> None:
        super().__init__(category_with_commodities_widget)
        self.category_with_commodities_widget = category_with_commodities_widget
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.category_group_box = QGroupBox()
        self.category_group_box.setObjectName("categoryGroupBox")
        box_layout = QVBoxLayout()
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.name_label.setFont(font)
        notes_layout = QFormLayout()
        self.notes_label = QLabel()
        self.notes_label.setObjectName("notesLabel")
        self.notes_edit = QTextEdit()
        button_layout = QHBoxLayout()
        self.update_category_button = QPushButton()
        self.update_category_button.setObjectName("updateCategoryButton")
        self.add_commodity_button = QPushButton()
        self.add_commodity_button.setObjectName("addCommodityButton")
        notes_layout.addRow(self.notes_label)
        notes_layout.addRow(self.notes_edit)
        button_layout.addStretch()
        button_layout.addWidget(self.update_category_button)
        button_layout.addWidget(self.add_commodity_button)
        box_layout.addWidget(self.name_label)
        box_layout.addLayout(notes_layout)
        box_layout.addLayout(button_layout)
        self.category_group_box.setLayout(box_layout)
        main_layout.addWidget(self.category_group_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_text_edit()

    def _setup_texts(self) -> None:
        widgets = [
            self.category_group_box,
            self.notes_label,
            self.update_category_button,
            self.add_commodity_button,
        ]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_text_edit(self) -> None:
        self.notes_edit.setReadOnly(True)
        self.notes_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.notes_edit.setAcceptRichText(False)
        self.notes_edit.setAcceptDrops(False)
        self.notes_edit.setUndoRedoEnabled(False)

    def set_category_texts(self, category: Category) -> None:
        self.name_label.setText(category.name)
        self.notes_edit.setText(category.notes or "")
