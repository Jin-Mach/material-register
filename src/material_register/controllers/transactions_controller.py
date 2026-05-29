from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

from material_register.init.data_init import DataInit
from material_register.ui.dialogs.create_transaction_dialog import CreateTransactionDialog

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


class TransactionsController:
    def __init__(self, transactions_widget: "TransactionsWidget") -> None:
        self.transactions_widget = transactions_widget

    def create_transaction(self) -> None:
        create_transaction_dialog = CreateTransactionDialog(self.transactions_widget, DataInit.customers_completer_model)
        if create_transaction_dialog.exec() == QDialog.DialogCode.Accepted:
            print("create data:", create_transaction_dialog.get_transaction_data())