from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

from material_register.db.queries.category_queries import CategoryQueries
from material_register.init.data_init import DataInit
from material_register.init.db_init import DbInit
from material_register.services.db_cache import DbCache
from material_register.ui.dialogs.category_commodity_dialog import CategoryCommodityDialog
from material_register.ui.dialogs.create_transaction_dialog import CreateTransactionDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.transaction_items_dialog import TransactionItemsDialogIn

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


class TransactionsController:
    def __init__(self, transactions_widget: "TransactionsWidget") -> None:
        self.transactions_widget = transactions_widget
        self.db_connection = DbInit.db_connection
        self.customers_model = DataInit.customers_model

    def create_transaction(self, transfer_type: str) -> None:
        create_data = self.create_transaction_data(transfer_type)
        if create_data is None:
            return
        if transfer_type == "IN":
            self.items_dialog = TransactionItemsDialogIn(self, create_data, self.transactions_widget, transfer_type)
        if self.items_dialog.exec() == QDialog.DialogCode.Accepted:
            print("OK")

    def create_transaction_data(self, transfer_type: str) -> dict[str, str | int | None] | None:
        if self.customers_model.get_total_count() == 0:
            MessageBoxes.show_error(self.transactions_widget, "NO_CUSTOMERS", "INFORMATION")
            return None
        dialog = CreateTransactionDialog(self.transactions_widget, DataInit.customers_completer_model, transfer_type)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        data = dialog.get_create_data()
        if transfer_type == "OUT":
            data.pop("paymentType", None)
        if not TransactionsController._check_data(data):
            MessageBoxes.show_error(self.transactions_widget, "INVALID_DATA", "WARNING")
            return None
        return data

    def create_category_commodity_data(self)-> dict[str, str | int | float] | None:
        categories_count = CategoryQueries.get_total_count(self.db_connection)
        if categories_count == 0:
            MessageBoxes.show_error(self.transactions_widget, "NO_CATEGORY", "INFORMATION")
            return None
        dialog = CategoryCommodityDialog(DbCache.categories, DbCache.commodities, self.items_dialog)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        data = dialog.get_category_commodity_data()
        if not TransactionsController._check_data(data):
            return None
        return data

    def update_category_commodity_data(self, item_data: dict[str, str | int | float]) -> dict[str, str | int | float] | None:
        dialog = CategoryCommodityDialog(DbCache.categories, DbCache.commodities, self.items_dialog)
        dialog.setup_update(item_data)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        data = dialog.get_category_commodity_data()
        if not TransactionsController._check_data(data):
            return None
        return data

    @staticmethod
    def _check_data(data: dict[str, str | int | float | None] | None) -> bool:
        if not data:
            return False
        for value in data.values():
            if value is None or value == "":
                return False
        return True