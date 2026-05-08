from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class CustomersActionsWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.setLayout(self._create_ui())
        self._ui_setup()

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        self.add_customer_button = QPushButton("Add Customer")
        self.add_customer_button.setObjectName("addCustomerButton")
        self.update_customer_button = QPushButton("Update Customer")
        self.update_customer_button.setObjectName("updateCustomerButton")
        self.active_customer_button = QPushButton("Deactivate Customer")
        self.active_customer_button.setObjectName("activeCustomerButton")
        main_layout.addWidget(self.add_customer_button)
        main_layout.addWidget(self.update_customer_button)
        main_layout.addWidget(self.active_customer_button)
        main_layout.addStretch()
        return main_layout

    def _ui_setup(self) -> None:
        if not UiTexts.set_ui_texts(self, [self.add_customer_button, self.update_customer_button,
                                           self.active_customer_button]):
            dialog = ErrorDialog()
            dialog.show_dialog("TEXTS_LOAD_FAILED", False)