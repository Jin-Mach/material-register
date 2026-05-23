from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QGroupBox, QFormLayout, QHBoxLayout, QPushButton

from material_register.domain.category_dataclass import Category


class CategoryDetailWidget(QWidget):
    def __init__(self, parent: QWidget=None) -> None:
        super().__init__(parent)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.category_group_box = QGroupBox("Category")
        self.category_group_box.setObjectName("CategoryGroupBox")
        box_layout = QVBoxLayout()
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.name_label.setFont(font)
        notes_layout = QFormLayout()
        self.notes_label = QLabel("Notes:")
        self.notes_label.setObjectName("notesLabel")
        self.notes_value = QTextEdit()
        self.notes_value.setReadOnly(True)
        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Update")
        notes_layout.addRow(self.notes_label)
        notes_layout.addRow(self.notes_value)
        button_layout.addStretch()
        button_layout.addWidget(self.update_button)
        box_layout.addWidget(self.name_label)
        box_layout.addLayout(notes_layout)
        box_layout.addLayout(button_layout)
        self.category_group_box.setLayout(box_layout)
        main_layout.addWidget(self.category_group_box)
        return main_layout

    def set_category_texts(self, category: Category) -> None:
        self.name_label.setText(category.name)
        self.notes_value.setText(category.notes or "")