from typing import TYPE_CHECKING

from PySide6.QtSql import QSqlDatabase
from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QDialog

from material_register.config.ui_constants import TRANSFER_IN, TRANSFER_OUT, PAYMENT_VALUES
from material_register.core.app_context import AppContext
from material_register.db.models.transaction_items_model_in import TransactionItemsModelIn
from material_register.db.queries.category_queries import CategoryQueries
from material_register.db.queries.transaction_items_queries import TransactionItemsQueries
from material_register.db.queries.transactions_queries import TransactionsQueries
from material_register.db.utils.date_filters import get_filter_range
from material_register.domain.transaction_dataclass import Transaction
from material_register.domain.transaction_item_detail_dataclass import TransactionItemDetail
from material_register.init.data_init import DataInit
from material_register.providers.texts_provider import TextsProvider
from material_register.services.db_cache import DbCache
from material_register.services.error_handler import ErrorHandler
from material_register.services.transactions_service import TransactionsService
from material_register.ui.dialogs.category_commodity_dialog import CategoryCommodityDialog
from material_register.ui.dialogs.create_transaction_dialog import CreateTransactionDialog
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.dialogs.notification_dialog import NotificationDialog
from material_register.ui.dialogs.transaction_items_dialog_in import TransactionItemsDialogIn
from material_register.ui.dialogs.transaction_items_dialog_out import TransactionItemsDialogOut
from material_register.db.models.transaction_items_model_out import TransactionItemsModelOut
from material_register.utils.normalizer import normalize_text

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget
    from material_register.db.models.transactions_load_model_in import TransactionsLoadModelIn
    from material_register.db.models.transactions_load_model_out import TransactionsLoadModelOut


class TransactionsController:
    def __init__(self, transactions_widget: "TransactionsWidget", db_connection: QSqlDatabase,
                 transactions_model_in: "TransactionsLoadModelIn",
                 transactions_model_out: "TransactionsLoadModelOut") -> None:
        self.transactions_widget = transactions_widget
        self.db_connection = db_connection
        self.transactions_model_in = transactions_model_in
        self.transactions_model_out = transactions_model_out
        self.customers_model = DataInit.customers_model
        self.inventory_model = DataInit.inventory_model
        self.notification_text = TextsProvider.NOTIFICATION_TEXTS.get("TRANSACTIONS", None)
        self.active_commodity_unit = None
        self.items_dialog = None
        self._models_map = {
            0: (self.transactions_model_in, TRANSFER_IN),
            1: (self.transactions_model_out, TRANSFER_OUT)
        }

    def create_transaction(self, transfer_type: str) -> None:
        create_data = self.create_transaction_data(transfer_type)
        if create_data is None:
            return
        if transfer_type == TRANSFER_IN:
            self.items_dialog = TransactionItemsDialogIn(self, create_data, self.transactions_widget, transfer_type)
        if transfer_type == TRANSFER_OUT:
            self.items_dialog = TransactionItemsDialogOut(self, create_data, self.transactions_widget, transfer_type)
        if self.items_dialog.exec() == QDialog.DialogCode.Accepted:
            self.active_commodity_unit = None
            dialog_data = self.items_dialog.return_transaction_data()
            model = self.items_dialog.transactions_items_widget.current_model
            if not TransactionsController._check_transaction_data(dialog_data, model):
                MessageBoxes.show_error(self.transactions_widget, "INVALID_DATA", "WARNING")
                return
            ok, error = TransactionsService.create_transaction(self.db_connection, dialog_data, model.get_data())
            if not ok:
                TransactionsController._handle_db_error(error, f"{self.__class__.__name__}.create_transaction")
                return
            self._refresh_models_data()
            self.inventory_model.load_inventory_data()
            self.items_dialog = None
            TransactionsController._notification_handler(self.notification_text, "ADD_TRANSACTION",
                                                         "Transaction added")

    def update_transaction(self, proxy_index: QModelIndex) -> None:
        tab_context = self._get_tab_context()
        if tab_context is None:
            return
        model, transaction_type = tab_context
        model_index = self.transactions_widget.active_proxy.mapToSource(proxy_index)
        if not model_index.isValid():
            return
        transaction = model.transaction_data[model_index.row()]
        transaction_id = transaction.transaction_id
        items_data = TransactionItemsQueries.get_transaction_items(self.db_connection, transaction_id)
        create_data = TransactionsController._transaction_to_dict(transaction)
        if transaction_type == TRANSFER_IN:
            self.items_dialog = TransactionItemsDialogIn(self, create_data, self.transactions_widget, transaction_type)
        if transaction_type == TRANSFER_OUT:
            self.items_dialog = TransactionItemsDialogOut(self, create_data, self.transactions_widget, transaction_type)
            self.active_commodity_unit = items_data[0].commodity_suffix
        item_model = self.items_dialog.transactions_items_widget.current_model
        if item_model is None:
            return
        TransactionsController._load_items_to_model(item_model, items_data)
        old_items_data = item_model.get_data()
        self.items_dialog.transactions_items_widget.setup_total_value(item_model)
        if self.items_dialog.exec() == QDialog.DialogCode.Accepted:
            self.active_commodity_unit = None
            dialog_data = self.items_dialog.return_transaction_data()
            if not TransactionsController._check_transaction_data(dialog_data, item_model):
                MessageBoxes.show_error(self.transactions_widget, "INVALID_DATA", "WARNING")
                return
            ok, error, changed = TransactionsService.update_transaction(self.db_connection, transaction_id,
                                                                        dialog_data, item_model.get_data(),
                                                                        old_items_data)
            if not ok:
                TransactionsController._handle_db_error(error, f"{self.__class__.__name__}.update_transaction")
                return
            if not changed:
                self.items_dialog = None
                return
            self._refresh_models_data()
            self.inventory_model.load_inventory_data()
            TransactionsController._notification_handler(self.notification_text, "UPDATE_TRANSACTION",
                                                         "Transaction updated")

    def delete_transaction(self, proxy_index: QModelIndex) -> None:
        tab_context = self._get_tab_context()
        if tab_context is None:
            return
        model, _ = tab_context
        model_index = self.transactions_widget.active_proxy.mapToSource(proxy_index)
        if not model_index.isValid():
            return
        transaction = model.transaction_data[model_index.row()]
        question = MessageBoxes.show_question(self.transactions_widget, "DELETE_TRANSACTION", transaction.customer_name)
        if question:
            transaction_id = transaction.transaction_id
            ok, error = TransactionsService.delete_transaction(self.db_connection, transaction_id,
                                                               transaction.transaction_type)
            if not ok:
                TransactionsController._handle_db_error(error, f"{self.__class__.__name__}.delete_transaction")
                return
            model.removeRow(model_index.row())
            self.inventory_model.load_inventory_data()
            self._update_counts()
            TransactionsController._notification_handler(self.notification_text, "DELETE_TRANSACTION",
                                                         "Transaction deleted")

    def create_transaction_data(self, transfer_type: str) -> dict[str, str | int | None] | None:
        if self.customers_model.get_total_count() == 0:
            MessageBoxes.show_error(self.transactions_widget, "NO_CUSTOMERS", "INFORMATION")
            return None
        dialog = CreateTransactionDialog(self.transactions_widget, DataInit.customers_completer_model, transfer_type)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        data = dialog.get_create_data()
        if transfer_type == TRANSFER_OUT:
            data.pop("paymentType", None)
        if not TransactionsController._check_data(data):
            MessageBoxes.show_error(self.transactions_widget, "INVALID_DATA", "WARNING")
            return None
        return data

    def create_category_commodity_data(self, transfer_type: str)-> dict[str, str | int | float] | None:
        categories_count = CategoryQueries.get_total_count(self.db_connection)
        if categories_count == 0:
            MessageBoxes.show_error(self.transactions_widget, "NO_CATEGORY", "INFORMATION")
            return None
        dialog = CategoryCommodityDialog(DbCache.categories, DbCache.commodities, self.items_dialog, transfer_type)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        data = dialog.get_category_commodity_data()
        if not TransactionsController._check_data(data):
            return None
        if transfer_type == TRANSFER_OUT:
            unit = data["commoditySuffix"]
            if self.active_commodity_unit is None:
                self.active_commodity_unit = unit
            elif self.active_commodity_unit != unit:
                MessageBoxes.show_error(
                    self.transactions_widget, "INVALID_COMMODITY_UNIT", "WARNING")
                return None
        return data

    def update_category_commodity_data(self, item_data: dict[str, str | int | float], transfer_type: str) -> dict[str, str | int | float] | None:
        dialog = CategoryCommodityDialog(DbCache.categories, DbCache.commodities, self.items_dialog, transfer_type)
        dialog.setup_update(item_data)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return None
        data = dialog.get_category_commodity_data()
        if not TransactionsController._check_data(data):
            return None
        model = self.items_dialog.transactions_items_widget.current_model
        if isinstance(model, TransactionItemsModelOut):
            unit = data["commoditySuffix"]
            if model.rowCount() == 1:
                self.active_commodity_unit = unit
                return data
            if self.active_commodity_unit != unit:
                MessageBoxes.show_error(self.transactions_widget, "INVALID_COMMODITY_UNIT", "WARNING")
                return None
        return data

    def on_item_deleted(self, transfer_type: str) -> None:
        if transfer_type != TRANSFER_OUT:
            return
        model = self.items_dialog.transactions_items_widget.current_model
        if isinstance(model, TransactionItemsModelOut) and model.rowCount() == 0:
            self.active_commodity_unit = None

    def set_basic_transactions_filter(self, key: str) -> None:
        tab_context = self._get_tab_context()
        if tab_context is None:
            return
        model, transaction_type = tab_context
        from_date, to_date = get_filter_range(key)
        filtered_data = TransactionsQueries.get_basic_filter_data(self.db_connection, transaction_type,
                                                                  from_date, to_date)
        model.set_basic_filter(filtered_data)
        self.transactions_widget.transactions_actions_widget.search_line_edit.clear()
        self.transactions_widget.transactions_proxy_filter_in.set_filtered_text("")
        self.transactions_widget.transactions_proxy_filter_out.set_filtered_text("")
        if not filtered_data:
            model.load_transactions_data()
        self._update_counts()

    def set_proxy_transactions_filter(self, search_text: str) -> None:
        text = normalize_text(search_text)
        proxy_model = self.transactions_widget.active_proxy
        if proxy_model is None:
            return
        proxy_model.set_filtered_text(text)
        if proxy_model.rowCount() == 0:
            self.transactions_widget.transactions_actions_widget.search_line_edit.selectAll()
            MessageBoxes.show_error(self.transactions_widget, "NO_RESULTS", "WARNING")
            proxy_model.set_filtered_text("")
            return
        self._update_counts()

    def reset_model_data(self) -> None:
        key = self.transactions_widget.transactions_actions_widget.get_filter_key()
        from_date, to_date = get_filter_range(key)
        for model, transaction_type in self._models_map.values():
            filtered_data = TransactionsQueries.get_basic_filter_data(self.db_connection, transaction_type,
                                                                      from_date, to_date)
            model.set_basic_filter(filtered_data)
        self.transactions_widget.transactions_actions_widget.search_line_edit.clear()
        self.transactions_widget.transactions_proxy_filter_in.set_filtered_text("")
        self.transactions_widget.transactions_proxy_filter_out.set_filtered_text("")
        self._update_counts()

    def _refresh_models_data(self) -> None:
        tab_context = self._get_tab_context()
        if tab_context is None:
            return
        model, transaction_type = tab_context
        key = self.transactions_widget.transactions_actions_widget.get_filter_key()
        from_date, to_date = get_filter_range(key)
        for model, transfer_type in self._models_map.values():
            filtered_data = TransactionsQueries.get_basic_filter_data(self.db_connection,transaction_type, from_date, to_date)
            model.set_basic_filter(filtered_data)
        self._update_counts()

    def _update_counts(self) -> None:
        current_tab = self.transactions_widget.transactions_tab_widget.currentIndex()
        if current_tab == 0:
            proxy = self.transactions_widget.transactions_proxy_filter_in
            model = self.transactions_model_in
        else:
            proxy = self.transactions_widget.transactions_proxy_filter_out
            model = self.transactions_model_out
        self.transactions_widget.set_count_text(proxy.rowCount(), model.rowCount())

    def _get_tab_context(self) -> tuple["TransactionsLoadModelIn | TransactionsLoadModelOut", str] | None:
        current_tab = self.transactions_widget.transactions_tab_widget.currentIndex()
        tab_context = self._models_map.get(current_tab)
        if tab_context is None:
            return None
        return tab_context

    @staticmethod
    def _check_data(data: dict[str, str | int | float | None] | None) -> bool:
        if not data:
            return False
        for value in data.values():
            if value is None or value == "":
                return False
        return True

    @staticmethod
    def _check_transaction_data(dialog_data: dict[str, str | int | None],
                                model: TransactionItemsModelIn | TransactionItemsModelOut) -> bool:
        if not TransactionsController._is_dialog_data_valid(dialog_data):
            return False
        if not isinstance(model, (TransactionItemsModelIn, TransactionItemsModelOut)):
            return False
        return bool(model.get_data())

    @staticmethod
    def _transaction_to_dict(transaction: Transaction) -> dict[str, str | int | float | None]:
        return {
            "paymentType": transaction.payment_type,
            "customerId": transaction.customer_id,
            "customer": transaction.customer_name,
            "documentNumber": transaction.customer_document_number,
            "address": transaction.customer_address,
            "notes": transaction.transaction_notes
        }

    @staticmethod
    def _load_items_to_model(model: TransactionItemsModelIn | TransactionItemsModelOut,
                             items: list[TransactionItemDetail]) -> None:
        for item in items:
            model.add_item({
                "category": item.category_name,
                "commodity": item.commodity_name,
                "commoditySuffix": item.commodity_suffix,
                "commodityId": item.commodity_id,
                "unitCount": item.unit_count,
                "pricePerUnit": item.price_per_unit,
            })

    @staticmethod
    def _is_dialog_data_valid(dialog_data: dict[str, str | int | None]) -> bool:
        for key, value in dialog_data.items():
            if key == "notes":
                continue
            if key == "payment_type":
                if value is not None and value not in PAYMENT_VALUES:
                    return False
                continue
            if value is None or value == "":
                return False
        return True

    @staticmethod
    def _handle_db_error(error: str, method: str) -> None:
        if not error:
            error = f"Unknown database error: {method}"
        ErrorHandler.handle_error(error, "db", "critical")
        dialog = ErrorDialog()
        dialog.show_dialog("DATABASE_ERROR", False)

    @staticmethod
    def _notification_handler(notification_texts: dict[str, str], key: str, default: str) -> None:
        if notification_texts is None:
            return
        notification = NotificationDialog(AppContext.MAIN_WINDOW, notification_texts.get(key, default))
        notification.show_notification()