from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QObject, QThread, QTimer
from PySide6.QtWidgets import QWidget

from material_register.db.queries.transaction_items_queries import (
    TransactionItemsQueries,
)
from material_register.domain.search_dataclass import (
    SearchResultsDataclass,
)
from material_register.domain.transaction_dataclass import Transaction
from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler
from material_register.services.filter_builder import FilterBuilder
from material_register.services.search_manager import SearchManager
from material_register.ui.config.ui_constants import LOG_LEVEL_CRITICAL, LOGGER_DB
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.ui.helpers.border_animation import BorderAnimation
from material_register.workers.search_worker import SearchWorker

if TYPE_CHECKING:
    from material_register.ui.search.search_widget import SearchWidget


class SearchController(QObject):
    def __init__(self, search_widget: "SearchWidget") -> None:
        super().__init__()
        self.search_widget = search_widget
        self.worker = None
        self.thread = None
        self._is_thread_running = False
        self.border_animation = None
        self._filters = None
        self._period_key = None
        self._last_value = []
        self._refresh = False
        self._refresh_exists = False

    def start_basic_filter(
        self,
        period_key: str | None,
        value: str,
        init: bool = False,
        refresh: bool = False,
    ) -> None:
        if self.thread is not None or self.worker is not None:
            return
        self._filters = (period_key, value)
        self._refresh = refresh
        where, params = FilterBuilder.create_basic_filter(period_key, value)
        if not init:
            self.search_widget.search_actions_widget.set_search_buttons_state(True)
            self.border_animation = BorderAnimation(
                self.search_widget.transactions_group_box
            )
            self.border_animation.start_animation()
        self._start_worker(where, params, init)

    def _start_worker(self, where: str, params: list[str], init: bool = False) -> None:
        self._is_thread_running = True
        self.thread = QThread()
        self.worker = SearchWorker(where, params, init)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._search_error)
        self.worker.finished.connect(self._search_ok)
        self.thread.start()

    def _search_error(self, error: str) -> None:
        self._clean_thread()
        QTimer.singleShot(100, lambda: self._finish_search(error=error))

    def _search_ok(self, results: SearchResultsDataclass, init: bool) -> None:
        self._clean_thread()
        QTimer.singleShot(100, lambda: self._finish_search(results=results, init=init))

    def _check_finish(self) -> None:
        if self.border_animation is None:
            return
        self.border_animation.search_finished = True
        if self.border_animation.progress >= self.border_animation.width():
            self._cleanup_border_animation()
        else:
            self.border_animation.finished.connect(self._cleanup_border_animation)

    def _cleanup_border_animation(self) -> None:
        if self.border_animation is None:
            return
        self.border_animation.stop_animation()
        self.border_animation.deleteLater()
        self.border_animation = None
        self.search_widget.search_actions_widget.set_search_buttons_state(False)

    def _clean_thread(self) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _reset_variables(self) -> None:
        self.worker = None
        self.thread = None
        self._is_thread_running = False

    def _finish_search(
        self,
        results: SearchResultsDataclass | None = None,
        error: str | None = None,
        init: bool = False,
    ) -> None:
        self._check_finish()
        self._reset_variables()
        try:
            if error is not None:
                SearchController._handle_search_error(
                    error,
                    f"{self.__class__.__name__}._search_error",
                    self.search_widget,
                )
                return
            if results is None:
                SearchController._handle_search_error(
                    "SearchResultsDataclass is None",
                    f"{self.__class__.__name__}._search_error",
                    self.search_widget,
                )
                return
            if not init and len(results.transactions) == 0 and not self._refresh:
                self.search_widget.search_actions_widget.search_line_edit.selectAll()
                self.search_widget.search_actions_widget.search_line_edit.setFocus()
                MessageBoxes.show_error(self.search_widget, "NO_RESULTS", "WARNING")
                return
            if len(results.transactions) == 0 and self._refresh:
                self.search_widget.search_transactions_model.load_data([])
                self.search_widget.search_material_model.load_data([])
                self.search_widget.set_count_text(0, results.transactions_count)
                self.search_widget.set_price_text(results.transactions_total_amount)
                self.search_widget.search_detail_widget.reset_data()
                return
            self._period_key = self._filters[0]
            self._last_value = self._filters[1]
            self._filters = None
            SearchManager.setup_last_controller(self.__class__.__name__)
            self.search_widget.search_detail_widget.reset_data()
            self.search_widget.search_detail_widget.tab_widget.setCurrentIndex(0)
            self.search_widget.search_tab_widget.setCurrentIndex(0)
            transactions = results.transactions
            transactions_count = results.transactions_count
            transactions_amount = results.transactions_total_amount
            materials = results.materials
            self.search_widget.search_transactions_model.load_data(transactions)
            self.search_widget.set_count_text(len(transactions), transactions_count)
            self.search_widget.set_price_text(transactions_amount)
            self.search_widget.search_material_model.load_data(materials)
        finally:
            if self._refresh_exists:
                self._refresh_exists = False
                QTimer.singleShot(0, self.refresh_filters_data)

    def update_transaction_detail_widget(self, proxy_index: QModelIndex) -> None:
        model_index = self.search_widget.search_proxy_model.mapToSource(proxy_index)
        if not model_index.isValid():
            return
        transaction = self.search_widget.search_transactions_model.transaction_data[
            model_index.row()
        ]
        if transaction.transaction_id is None:
            return
        items_data = TransactionItemsQueries.get_transaction_items(
            DbInit.db_connection, transaction.transaction_id
        )
        if items_data is None:
            SearchController._handle_search_error(
                "Transaction items could not be loaded",
                f"{self.__class__.__name__}.update_transaction_detail_widget",
                self.search_widget,
                "DATABASE_ERROR",
            )
            return
        create_data = self._transaction_to_dict(transaction)
        self.search_widget.search_detail_widget.update_data(
            create_data,
            items_data,
            transaction.transaction_type,
        )

    def refresh_filters_data(self) -> None:
        if self._is_thread_running:
            self._refresh_exists = True
            return
        self.start_basic_filter(self._period_key, self._last_value, refresh=True)

    def shut_down(self) -> None:
        if self.thread is None:
            return
        self.thread.quit()
        self.thread.wait()

    @staticmethod
    def _transaction_to_dict(transaction: Transaction) -> dict[str, str | int | bool]:
        return {
            "paymentType": transaction.payment_type,
            "isInvoiced": transaction.is_invoiced,
            "customerId": transaction.customer_id,
            "customer": transaction.customer_name,
            "documentNumber": transaction.customer_document_number,
            "address": transaction.customer_address,
            "notes": transaction.transaction_notes,
        }

    @staticmethod
    def _handle_search_error(
        error: str, method: str, parent: QWidget, error_key: str = "SEARCH_ERROR"
    ) -> None:
        if not error:
            error = f"Unknown search error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", LOGGER_DB, LOG_LEVEL_CRITICAL)
        ErrorDialog(parent).show_dialog(error_key, False)
