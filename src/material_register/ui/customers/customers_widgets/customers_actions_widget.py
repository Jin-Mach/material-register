from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

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
        self.update_customer_button = QPushButton("Update")
        self.update_customer_button.setObjectName("updateCustomerButton")
        self.active_customer_button = QPushButton("Active")
        self.active_customer_button.setObjectName("activeCustomerButton")
        main_layout.addWidget(self.add_customer_button)
        main_layout.addWidget(self.update_customer_button)
        main_layout.addWidget(self.active_customer_button)
        main_layout.addStretch()
        return main_layout

    def _ui_setup(self) -> None:
        if not UiTexts.set_ui_texts(self, [self.add_customer_button, self.update_customer_button,
                                           self.active_customer_button]):
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return