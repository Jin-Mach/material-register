from typing import TYPE_CHECKING

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QShowEvent, QRegularExpressionValidator
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QTextEdit, QHBoxLayout, QDialogButtonBox


from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


# noinspection PyTypeChecker
class CategoryDialog(QDialog):
    ADD_MODE = "ADD"
    UPDATE_MODE = "UPDATE"
    NOTES_LENGTH = 200

    def __init__(self, catalog_widget: "CatalogWidget", mode: str = ADD_MODE, category_data: dict | None = None) -> None:
        super().__init__(catalog_widget)
        self.catalog_widget = catalog_widget
        self.mode = mode
        self.category_data = category_data
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()
        self._update_save_button_state()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.category_name_label = QLabel()
        self.category_name_label.setObjectName("categoryNameLabel")
        self.category_name_input = QLineEdit()
        self.category_name_input.setObjectName("categoryNameInput")
        self.notes_label = QLabel()
        self.notes_label.setObjectName("notesLabel")
        self.notes_input = QTextEdit()
        notes_count_layout = QHBoxLayout()
        self.notes_count_label = QLabel()
        self.notes_count_label.setObjectName("notesCountLabel")
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Close)
        self.save_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.save_button.setObjectName("saveButton")
        self.close_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.close_button.setObjectName("closeButton")
        notes_count_layout.addWidget(self.notes_count_label)
        notes_count_layout.addStretch()
        main_layout.addWidget(self.category_name_label)
        main_layout.addWidget(self.category_name_input)
        main_layout.addWidget(self.notes_label)
        main_layout.addWidget(self.notes_input)
        main_layout.addLayout(notes_count_layout)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [self.category_name_label, self.notes_label, self.notes_count_label, self.save_button,
                   self.close_button]
        self._setup_texts(widgets)
        self._setup_mode()
        self._set_validators()

    def _create_connection(self) -> None:
        self.category_name_input.textChanged.connect(self._on_form_changed)
        self.notes_input.textChanged.connect(self._update_notes_count)
        self.save_button.clicked.connect(self.accept)
        self.close_button.clicked.connect(self.reject)

    def _setup_texts(self, widgets: list) -> None:
        texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.notes_count_text = texts.get(f"{self.notes_count_label.objectName()}Text", "Count:")
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_mode(self) -> None:
        if self.mode == self.ADD_MODE:
            self._set_add_mode()
        elif self.mode == self.UPDATE_MODE and self.category_data:
            self._set_update_mode(self.category_data)

    def _set_validators(self) -> None:
        category_validator = QRegularExpressionValidator(QRegularExpression(r"[\p{L}0-9 .,&\-\/]{1,30}"))
        self.category_name_input.setValidator(category_validator)

    def _set_add_mode(self) -> None:
        self.category_name_input.clear()
        self.notes_input.clear()
        self._update_notes_count()

    def _set_update_mode(self, category_data: dict) -> None:
        self.category_name_input.setText(category_data.get("name", ""))
        self.notes_input.setPlainText(category_data.get("notes", ""))
        self._update_notes_count()

    def _update_notes_count(self) -> None:
        text = self.notes_input.toPlainText()
        if len(text) > self.NOTES_LENGTH:
            text = text[:self.NOTES_LENGTH]
            self.notes_input.blockSignals(True)
            self.notes_input.setPlainText(text)
            self.notes_input.blockSignals(False)
            cursor = self.notes_input.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.notes_input.setTextCursor(cursor)
        self.notes_count_label.setText(f"{self.notes_count_text} {len(text)}/{self.NOTES_LENGTH}")

    def _update_save_button_state(self) -> None:
        self.save_button.setEnabled(self._is_input_valid() and self._is_category_valid())

    def _on_form_changed(self) -> None:
        self._update_save_button_state()

    def _is_input_valid(self) -> bool:
        category_name = self.category_name_input.text().strip()
        return bool(category_name)

    def _is_category_valid(self) -> bool:
        category_name = self.category_name_input.text().strip()
        if not category_name:
            return False
        ignored_id = None
        if self.mode != self.ADD_MODE and self.category_data:
            ignored_id = self.category_data.get("id")
        return not self.catalog_widget.catalog_controller.category_exists(category_name, ignored_id=ignored_id)

    def get_category_data(self) -> dict | None:
        if not self._is_input_valid():
            return None
        return {"name": self.category_name_input.text().strip(), "notes": self.notes_input.toPlainText().strip(),}

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.adjustSize()
        self.setFixedSize(self.size())
        centre_dialog(self)