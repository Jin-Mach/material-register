from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.customers.customers_widget import CustomersWidget

class CustomersActionsWidget(QWidget):
    def __init__(self, customer_widget: "CustomersWidget") -> None:
        super().__init__(customer_widget)
        self.setLayout(self._create_ui())
        self._ui_setup()

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        self.add_customer_button = QPushButton("Add")
        self.add_customer_button.setObjectName("addCustomerButton")
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setObjectName("searchLineEdit")
        self.search_line_edit.setMinimumWidth(600)
        main_layout.addWidget(self.add_customer_button)
        main_layout.addStretch()
        main_layout.addWidget(self.search_line_edit)
        main_layout.addStretch()
        return main_layout

    def _ui_setup(self) -> None:
        widgets = [self.add_customer_button, self.search_line_edit]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return