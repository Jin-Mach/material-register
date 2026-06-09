from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu


if TYPE_CHECKING:
    from material_register.ui.customers.customers_widgets.customers_view import CustomersView
    from material_register.controllers.customers_controller import CustomersController


class CustomersContextMenu(QMenu):
    def __init__(self, customers_view: "CustomersView", customers_controller: "CustomersController") -> None:
        super().__init__(customers_view)
        self.customers_controller = customers_controller
        self._create_ui()
        self.create_connection()
        self.customer_index = None

    def _create_ui(self) -> None:
        self.update_customer_action = QAction(self)
        self.update_customer_action.setObjectName("updateCustomerAction")
        self.active_customer_action = QAction(self)
        self.active_customer_action.setObjectName("activeCustomerAction")
        self.addAction(self.update_customer_action)
        self.addAction(self.active_customer_action)

    def set_ui_texts(self, ui_texts: dict[str, str]) -> None:
        if ui_texts:
            for widget in self.findChildren(QAction):
                key = widget.objectName() + "Text"
                if key in ui_texts:
                    widget.setText(ui_texts[key])

    def create_connection(self) -> None:
        self.update_customer_action.triggered.connect(self._update_customer)
        self.active_customer_action.triggered.connect(self._change_customer_active)

    def set_customer_index(self, index: QModelIndex) -> None:
        self.customer_index = index

    def _update_customer(self) -> None:
        if self.customer_index is None:
            return
        self.customers_controller.update_customer(self.customer_index)

    def _change_customer_active(self) -> None:
        if self.customer_index is None:
            return
        self.customers_controller.change_customer_active(self.customer_index)