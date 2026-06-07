from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QDialog, QMessageBox

from material_register.db.utils.customers_filter_helper import CustomersFilterHelper
from material_register.core.app_context import AppContext
from material_register.domain.customers_dataclass import Customer
from material_register.init.data_init import DataInit
from material_register.providers.texts_provider import TextsProvider
from material_register.services.db_cache import DbCache
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.customer_dialog import CustomerDialog
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.notification_dialog import NotificationDialog
from material_register.utils.normalizer import normalize_text, normalize_whitespace

if TYPE_CHECKING:
    from material_register.ui.customers.customers_widget import CustomersWidget
    from material_register.db.models.customers_model import CustomersModel


class CustomersController:
    def __init__(self, customers_widget: "CustomersWidget") -> None:
        self.customers_model = DataInit.customers_model
        self.customers_widget = customers_widget
        self.notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("CUSTOMERS", None)

    def add_customer(self) -> None:
        dialog = CustomerDialog(self.customers_widget)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            customer = dialog.get_customer_data()
            if customer is None:
                dialog = ErrorDialog()
                dialog.show_dialog("UNKNOWN_ERROR", False)
                return
            CustomersController._normalize_customer(customer)
            if not self.customers_model.add_customer(customer):
                CustomersController._handle_db_error(self.customers_model, f"{self.__class__.__name__}.add_customers")
                return
            CustomersController._refresh_cache()
            self.update_counts()
            CustomersController._notification_handler(self.notification_texts, "ADD_CUSTOMER", "Customer added")

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
                CustomersController._handle_db_error(self.customers_model, f"{self.__class__.__name__}.update_customers")
                return
            CustomersController._refresh_cache()
            CustomersController._notification_handler(self.notification_texts, "UPDATE_CUSTOMER", "Record updated")

    def change_customer_active(self, customer_index: QModelIndex) -> None:
        customer_id = CustomersController._get_id_from_index(customer_index)
        if customer_id == -1:
            return
        customer_data = self.customers_model.get_customer_by_id(customer_id)
        customer_name = CustomersController._handle_customer_name(customer_data)
        question = MessageBoxes.show_question(self.customers_widget, "ACTIVE", customer_name)
        if question:
            if not self.customers_model.set_active(customer_id, not customer_data.active):
                CustomersController._handle_db_error(self.customers_model, f"{self.__class__.__name__}.set_active")
                return
            CustomersController._refresh_cache()
            CustomersController._notification_handler(self.notification_texts, "CHANGE_ACTIVE", "Status changed")

    def filter_customers(self, search_text: str) -> None:
        normalized_text = normalize_text(search_text)
        final_filter = CustomersFilterHelper.get_filter(normalized_text)
        self.customers_model.setFilter(final_filter)
        if self.customers_model.rowCount() == 0:
            self.update_counts()
            MessageBoxes.show_error(self.customers_widget, "CUSTOMER_NOT_FOUND", "WARNING")
            self.customers_widget.action_widget.search_line_edit.clear()
            self.customers_model.setFilter("")
        self.update_counts()

    def update_counts(self) -> None:
        filtered = self.customers_model.rowCount()
        total = self.customers_model.get_total_count()
        self.customers_widget.set_count_text(filtered, total)

    @staticmethod
    def _refresh_cache() -> None:
        DbCache.refresh_catalog_data()
        DataInit.customers_completer_model.reload_customers(DbCache.active_customers)

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

    @staticmethod
    def _handle_db_error(model: "CustomersModel", method: str) -> None:
        error = model.lastError().text()
        if not error:
            error = f"Unknown database error: {method}"
        ErrorHandler.handle_error(error, "db", "critical")
        dialog = ErrorDialog()
        dialog.show_dialog("DATABASE_ERROR", False)

    @staticmethod
    def _handle_customer_name(customer: Customer) -> str:
        if not customer.company:
            return customer.first_name + " " + customer.last_name
        return customer.company

    @staticmethod
    def _notification_handler(notification_texts: dict[str, str], key: str, default: str) -> None:
        if notification_texts is None:
            return
        notification = NotificationDialog(AppContext.MAIN_WINDOW, notification_texts.get(key, default))
        notification.show_notification()