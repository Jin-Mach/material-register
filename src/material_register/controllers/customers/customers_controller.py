from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

from material_register.init.models_init import ModelsSetup
from material_register.ui.dialogs.customer_dialog import CustomerDialog

if TYPE_CHECKING:
    from material_register.ui.customers.customers_widget import CustomersWidget


class CustomersController:
    def __init__(self, customers_widget: "CustomersWidget") -> None:
        self.customers_model = ModelsSetup.customers_model
        self.customers_widget = customers_widget

    def add_customers(self) -> None:
        dialog = CustomerDialog(self.customers_widget)
        dialog.centre_dialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            customer = dialog.get_customer_data()
            if customer is None:
                print("show dialog")
                return
            print("customer", customer)
            return
            #self.customers_model.add_customer(customer)