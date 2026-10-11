from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QObject, QThread, QTimer
from PySide6.QtWidgets import QWidget

from material_register.db.queries.transaction_items_queries import (
    TransactionItemsQueries,
)
from material_register.domain.branch_dataclass import BranchDataclass
from material_register.domain.search_dataclass import SearchDataclass
from material_register.domain.transaction_dataclass import Transaction
from material_register.domain.transaction_item_detail_dataclass import (
    TransactionItemDetail,
)
from material_register.init.db_init import DbInit
from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_CRITICAL,
    LOGGER_EXPORT,
)
from material_register.ui.dialogs.document_preview_dialog import DocumentPreviewDialog
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.setup.ui_settings import UiSettings
from material_register.workers.export_workers.pdf.documents.transaction_document_worker import (
    TransactionDocumentWorker,
)

if TYPE_CHECKING:
    from material_register.ui.search.search_widget import SearchWidget


class SearchDocumentController(QObject):
    def __init__(self, search_widget: "SearchWidget") -> None:
        super().__init__()
        self.search_widget = search_widget
        self.db_connection = DbInit.db_connection
        self.thread = None
        self.worker = None
        self.transaction_id = None
        self.export_texts = TextsProvider.EXPORT_TEXTS

    def create_pdf_document(self, proxy_index: QModelIndex) -> None:
        if not self.export_texts:
            self._handle_export_error(
                "Export texts not loaded",
                f"{self.__class__.__name__}.create_pdf_document",
                self.search_widget,
                "TEXTS_LOAD_FAILED",
            )
            return
        model = self.search_widget.search_transactions_model
        proxy_model = self.search_widget.search_proxy_model
        model_index = proxy_model.mapToSource(proxy_index)
        if not model_index.isValid():
            return
        transaction = self._prepare_transaction_dataclass(
            model.transaction_data[model_index.row()]
        )
        self.transaction_id = transaction.transaction_id
        transaction_type = transaction.transaction_type
        if self.transaction_id is None:
            self._handle_export_error(
                "Transaction ID is missing",
                f"{self.__class__.__name__}.create_pdf_document",
                self.search_widget,
            )
            return
        items_data = TransactionItemsQueries.get_transaction_items(
            self.db_connection, self.transaction_id
        )
        if not items_data:
            self._handle_export_error(
                "Transaction items could not be loaded",
                f"{self.__class__.__name__}.create_pdf_document",
                self.search_widget,
            )
            self.transaction_id = None
            return
        branch_settings = UiSettings.get_branch_settings()
        self._start_worker(
            transaction,
            items_data,
            transaction_type,
            branch_settings,
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
            self._handle_export_error(
                error,
                f"{self.__class__.__name__}._document_error",
                self.search_widget,
            )
            self._reset_variables()
            return
        preview_dialog = DocumentPreviewDialog(self.search_widget)
        preview_dialog.load_pdf_from_bytes(pdf_document, self.transaction_id)
        preview_dialog.exec()
        self._reset_variables()

    @staticmethod
    def _prepare_transaction_dataclass(search_data: SearchDataclass) -> Transaction:
        return Transaction(
            transaction_id=search_data.transaction_id,
            transaction_type=search_data.transaction_type,
            transaction_created_at=search_data.transaction_created_at,
            payment_type=search_data.payment_type,
            is_invoiced=search_data.is_invoiced,
            customer_id=search_data.customer_id,
            customer_document_number=search_data.customer_document_number,
            customer_address=search_data.customer_address,
            customer_name=search_data.customer_name,
            transaction_notes=search_data.transaction_notes,
            total=search_data.total,
            suffix=search_data.suffix,
        )

    @staticmethod
    def _handle_export_error(
        error: str,
        method: str,
        parent: QWidget,
        error_key: str = "DOCUMENT_ERROR",
    ) -> None:
        if not error:
            error = f"Unknown document error: {method}"
        ErrorHandler.handle_error(
            f"{error}: {method}",
            LOGGER_EXPORT,
            LOG_LEVEL_CRITICAL,
        )
        ErrorDialog(parent).show_dialog(error_key, False)
