from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QObject, QThread, QTimer
from PySide6.QtWidgets import QWidget

from material_register.db.queries.transaction_items_queries import (
    TransactionItemsQueries,
)
from material_register.domain.branch_dataclass import BranchDataclass
from material_register.domain.transaction_dataclass import Transaction
from material_register.domain.transaction_item_detail_dataclass import (
    TransactionItemDetail,
)
from material_register.init.db_init import DbInit
from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.ui.dialogs.document_preview_dialog import DocumentPreviewDialog
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.setup.ui_settings import UiSettings
from material_register.workers.export_workers.pdf.documents.transaction_document_worker import (
    TransactionDocumentWorker,
)

if TYPE_CHECKING:
    from material_register.db.models.transactions_load_model_in import (
        TransactionsLoadModelIn,
    )
    from material_register.db.models.transactions_load_model_out import (
        TransactionsLoadModelOut,
    )
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


class TransactionDocumentController(QObject):
    def __init__(
        self,
        transactions_widget: "TransactionsWidget",
        transactions_model_in: "TransactionsLoadModelIn",
        transactions_model_out: "TransactionsLoadModelOut",
    ) -> None:
        super().__init__()
        self.transactions_widget = transactions_widget
        self.db_connection = DbInit.db_connection
        self.transactions_model_in = transactions_model_in
        self.transactions_model_out = transactions_model_out
        self.thread = None
        self.worker = None
        self.transaction_id = None
        self.export_texts = TextsProvider.EXPORT_TEXTS
        self.branch_settings = UiSettings.get_branch_settings()
        self._models_map = {
            0: (self.transactions_model_in, TRANSFER_IN),
            1: (self.transactions_model_out, TRANSFER_OUT),
        }

    def create_pdf_document(self, proxy_index: QModelIndex) -> None:
        tab_context = self._get_tab_context()
        if tab_context is None:
            return
        if not self.export_texts:
            TransactionDocumentController._handle_export_error(
                "Export texts not loaded",
                f"{self.__class__.__name__}.create_pdf_document",
                self.transactions_widget,
                "TEXTS_LOAD_FAILED",
            )
            return
        model, transaction_type = tab_context
        model_index = self.transactions_widget.active_proxy.mapToSource(proxy_index)
        if not model_index.isValid():
            return
        transaction = model.transaction_data[model_index.row()]
        self.transaction_id = transaction.transaction_id
        items_data = TransactionItemsQueries.get_transaction_items(
            self.db_connection, self.transaction_id
        )
        self._start_worker(
            transaction,
            items_data,
            transaction_type,
            self.branch_settings,
            self.export_texts,
        )

    def _start_worker(
        self,
        transaction: Transaction,
        items_data: list[TransactionItemDetail],
        transfer_type: str,
        branch_settings: BranchDataclass,
        export_texts: dict[str, dict[str, str]],
    ) -> None:
        self.thread = QThread()
        self.worker = TransactionDocumentWorker(
            transaction,
            items_data,
            transfer_type,
            branch_settings,
            export_texts,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._export_error)
        self.worker.finished.connect(self._export_ok)
        self.thread.start()

    def _export_error(self, error: str) -> None:
        self._clean_thread()
        QTimer.singleShot(1000, lambda: self._finish_export(error=error))

    def _export_ok(self, pdf_document: bytes) -> None:
        self._clean_thread()
        self._finish_export(pdf_document=pdf_document)

    def _clean_thread(self) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _reset_variables(self) -> None:
        self.thread = None
        self.worker = None
        self.transaction_id = None

    def _finish_export(
        self, pdf_document: bytes | None = None, error: str | None = None
    ) -> None:
        if error is not None:
            TransactionDocumentController._handle_export_error(
                error,
                f"{self.__class__.__name__}._document_error",
                self.transactions_widget,
            )
            self._reset_variables()
            return
        preview_dialog = DocumentPreviewDialog(self.transactions_widget)
        preview_dialog.load_pdf_from_bytes(pdf_document, self.transaction_id)
        preview_dialog.exec()
        self._reset_variables()

    def _get_tab_context(
        self,
    ) -> tuple["TransactionsLoadModelIn | TransactionsLoadModelOut", str] | None:
        current_tab = self.transactions_widget.transactions_tab_widget.currentIndex()
        tab_context = self._models_map.get(current_tab)
        if tab_context is None:
            return None
        return tab_context

    @staticmethod
    def _handle_export_error(
        error: str, method: str, parent: QWidget, error_key: str = "DOCUMENT_ERROR"
    ) -> None:
        if not error:
            error = f"Unknown document error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", "export", "critical")
        ErrorDialog(parent).show_dialog(error_key, False)
