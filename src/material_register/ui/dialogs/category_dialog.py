from typing import TYPE_CHECKING

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QRegularExpressionValidator, QShowEvent
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
)

from material_register.config.ui_constants import (
    ADD_MODE,
    CATEGORY_DIALOG_NOTES_LENGTH,
    UPDATE_MODE,
)
from material_register.domain.category_dataclass import Category
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.notes_length_handler import check_notes_length
from material_register.ui.helpers.styles import INVALID_INPUT_STYLE
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


# noinspection PyTypeChecker
class CategoryDialog(QDialog):
    def __init__(
        self,
        catalog_widget: "CatalogWidget",
        mode: str = ADD_MODE,
        category_data: Category | None = None,
    ) -> None:
        super().__init__(catalog_widget)
        self.catalog_widget = catalog_widget
        self.mode = mode
        self.category_data = category_data
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.category_name_label = QLabel()
        self.category_name_label.setObjectName("categoryNameLabel")
        self.category_name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.category_name_input = QLineEdit()
        self.category_name_input.setObjectName("categoryNameInput")
        self.notes_label = QLabel()
        self.notes_label.setObjectName("notesLabel")
        self.notes_input = QTextEdit()
        notes_count_layout = QHBoxLayout()
        self.notes_count_label = QLabel()
        self.notes_count_label.setObjectName("notesCountLabel")
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Close
        )
        self.save_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.save_button.setObjectName("saveButton")
        self.close_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.close_button.setObjectName("closeButton")
        self.close_button.setDefault(True)
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
        self._setup_texts()
        self._setup_mode()
        self._set_validators()
        self._set_required_style(self.category_name_input)
        self._update_save_button_state()

    def _setup_texts(self) -> None:
        widgets = [
            self.category_name_label,
            self.notes_label,
            self.notes_count_label,
            self.save_button,
            self.close_button,
        ]
        texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.notes_count_text = texts.get(
            f"{self.notes_count_label.objectName()}Text", "Count:"
        )
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.category_name_input.textChanged.connect(self._on_form_changed)
        self.notes_input.textChanged.connect(self._update_notes_count)
        self.save_button.clicked.connect(self.accept)
        self.close_button.clicked.connect(self.reject)

    def _setup_mode(self) -> None:
        if self.mode == ADD_MODE:
            self._set_add_mode()
        elif self.mode == UPDATE_MODE and self.category_data:
            self._set_update_mode(self.category_data)

    def _set_validators(self) -> None:
        category_validator = QRegularExpressionValidator(
            QRegularExpression(r"[\p{L}0-9 .,:&%\-\/]{1,30}")
        )
        self.category_name_input.setValidator(category_validator)

    def _set_add_mode(self) -> None:
        self.category_name_input.clear()
        self.notes_input.clear()
        self._update_notes_count()

    def _set_update_mode(self, category_data: Category) -> None:
        self.category_name_input.setText(category_data.name or "")
        self.notes_input.setPlainText(category_data.notes or "")
        self._update_notes_count()

    def _update_notes_count(self) -> None:
        check_notes_length(
            self.notes_input,
            self.notes_count_label,
            self.notes_count_text,
            CATEGORY_DIALOG_NOTES_LENGTH,
        )

    def _update_save_button_state(self) -> None:
        self.save_button.setEnabled(
            self._is_input_valid() and self._is_category_valid()
        )

    def _set_required_style(self, widget) -> None:
        text = widget.text().strip()
        if widget == self.category_name_input:
            invalid = (
                not text
            ) or self.catalog_widget.catalog_controller.category_exists(
                text,
                ignored_id=self.category_data.id if self.mode == UPDATE_MODE else None,
            )
        else:
            invalid = not text
        if invalid:
            widget.setStyleSheet(INVALID_INPUT_STYLE)
        else:
            widget.setStyleSheet("")

    def _on_form_changed(self) -> None:
        self._set_required_style(self.category_name_input)
        self._update_save_button_state()

    def _is_input_valid(self) -> bool:
        category_name = self.category_name_input.text().strip()
        return bool(category_name)

    def _is_category_valid(self) -> bool:
        name = self.category_name_input.text().strip()
        if not name:
            return False
        ignored_id = None
        if self.mode == UPDATE_MODE and self.category_data:
            ignored_id = self.category_data.id
        return not self.catalog_widget.catalog_controller.category_exists(
            name, ignored_id=ignored_id
        )

    def get_category_data(self) -> Category | None:
        if not self._is_input_valid():
            return None
        return Category(
            name=self.category_name_input.text().strip(),
            notes=self.notes_input.toPlainText(),
        )

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.adjustSize()
        self.setFixedSize(self.size())
        centre_dialog(self)
