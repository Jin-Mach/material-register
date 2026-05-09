from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

from material_register.domain.customers_dataclass import Customer
from material_register.init.models_init import ModelsSetup
from material_register.ui.dialogs.customer_dialog import CustomerDialog
from material_register.utils.normalizer import normalize_text, normalize_whitespace

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
            CustomersController._normalize_customer(customer)
            print("customer:", customer)
            #self.customers_model.add_customer(customer)

    @staticmethod
    def _normalize_customer(customer: Customer) -> None:
        customer.company = normalize_whitespace(customer.company)
        customer.first_name = normalize_whitespace(customer.first_name)
        customer.last_name = normalize_whitespace(customer.last_name)
        customer.document_number = normalize_whitespace(customer.document_number)
        customer.address = normalize_whitespace(customer.address)
        customer.company_normalized = normalize_text(customer.company)
        customer.first_name_normalized = normalize_text(customer.first_name)
        customer.last_name_normalized = normalize_text(customer.last_name)
        customer.address_normalized = normalize_text(customer.address)