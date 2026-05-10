from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QDialog

from material_register.domain.customers_dataclass import Customer
from material_register.init.models_init import ModelsSetup
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.customer_dialog import CustomerDialog
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.utils.normalizer import normalize_text, normalize_whitespace

if TYPE_CHECKING:
    from material_register.ui.customers.customers_widget import CustomersWidget


class CustomersController:
    def __init__(self, customers_widget: "CustomersWidget") -> None:
        self.customers_model = ModelsSetup.customers_model
        self.customers_widget = customers_widget

    def add_customers(self) -> None:
        dialog = CustomerDialog(self.customers_widget)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            customer = dialog.get_customer_data()
            if customer is None:
                dialog = ErrorDialog()
                dialog.show_dialog("UNKNOWN_ERROR", False)
                return
            CustomersController._normalize_customer(customer)
            if not self.customers_model.add_customer(customer):
                error = self.customers_model.lastError().text()
                if not error:
                    error = f"Unknown database error: {self.__class__.__name__}.add_customers"
                ErrorHandler.handle_error(error, "db", "critical")
                dialog = ErrorDialog()
                dialog.show_dialog("DATABASE_ERROR", False)
        self.customers_widget.customers_view.update_headers(self.customers_model)

    def update_customer(self, customer_index: QModelIndex) -> None:
        customer_id = CustomersController._get_id_from_index(customer_index)
        if customer_id == -1:
            return
        customer_data = self.customers_model.get_customer_by_id(customer_id)
        dialog = CustomerDialog(self.customers_widget, mode="UPDATE", customer_data=customer_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            customer = dialog.get_customer_data()
            if customer is None:
                dialog = ErrorDialog()
                dialog.show_dialog("UNKNOWN_ERROR", False)
                return
            CustomersController._normalize_customer(customer)
            if not self.customers_model.update_customer(customer_id, customer):
                error = self.customers_model.lastError().text()
                if not error:
                    error = f"Unknown database error: {self.__class__.__name__}.update_customers"
                ErrorHandler.handle_error(error, "db", "critical")
                dialog = ErrorDialog()
                dialog.show_dialog("DATABASE_ERROR", False)
        self.customers_widget.customers_view.update_headers(self.customers_model)

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

    @staticmethod
    def _get_id_from_index(index: QModelIndex) -> int:
        customer_id = index.data(Qt.ItemDataRole.UserRole)
        if customer_id is None or customer_id < 0:
            return -1
        return customer_id