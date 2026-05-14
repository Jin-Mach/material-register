from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.customers.customers_widgets.customers_view import CustomersView


class CustomersTabWidget(QWidget):
    def __init__(self, customers_view: "CustomersView", parent=None) -> None:
        super().__init__(parent)
        self.customers_view = customers_view
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.count_layout = QHBoxLayout()
        self.count_label = QLabel()
        self.count_label.setObjectName("countLabel")
        self.count_layout.addWidget(self.count_label)
        self.count_layout.addStretch()
        main_layout.addWidget(self.customers_view)
        main_layout.addLayout(self.count_layout)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        if self.count_text == "":
            self.count_label.hide()

    def _setup_texts(self) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            self.count_text = ""
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.count_text = ui_texts.get(f"{self.count_label.objectName()}Text", "")

    def set_count_text(self, filtered: int, total: int) -> None:
        self.count_label.setText(f"{self.count_text} {filtered}/{total}")