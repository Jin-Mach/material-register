from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

from material_register.init.data_init import DataInit
from material_register.services.db_cache import DbCache
from material_register.ui.dialogs.category_commodity_dialog import CategoryCommodityDialog
from material_register.ui.dialogs.create_transaction_dialog import CreateTransactionDialog
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.transaction_items_dialog import TransactionItemsDialog

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


class TransactionsController:
    def __init__(self, transactions_widget: "TransactionsWidget") -> None:
        self.transactions_widget = transactions_widget

    def create_transaction(self) -> None:
        create_data = self.create_transaction_data()
        if create_data is None:
            return
        self.items_dialog = TransactionItemsDialog(self, create_data, self.transactions_widget)
        if self.items_dialog.exec() == QDialog.DialogCode.Accepted:
            print("OK")

    def create_transaction_data(self) -> dict[str, str | int | None] | None:
        dialog = CreateTransactionDialog(self.transactions_widget, DataInit.customers_completer_model)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        data = dialog.get_create_data()
        if not TransactionsController._check_data(data):
            dialog = ErrorDialog()
            dialog.show_dialog("UNKNOWN_ERROR", False)
            return None
        return data

    def create_category_commodity_data(self)-> dict[str, str | int | float] | None:
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