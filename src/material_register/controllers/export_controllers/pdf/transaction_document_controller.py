from PySide6.QtCore import QObject, QThread, QTimer

from material_register.domain.transaction_dataclass import Transaction
from material_register.domain.transaction_item_detail_dataclass import (
    TransactionItemDetail,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.transactions.transactions_widget import TransactionsWidget
from material_register.workers.export_workers.pdf.documents.transaction_document_worker import (
    TransactionDocumentWorker,
)


class TransactionDocumentController(QObject):
    def __init__(self, transactions_widget: TransactionsWidget) -> None:
        super().__init__()
        self.transactions_widget = transactions_widget
        self.thread = None
        self.worker = None

    def create_pdf_document(
        self,
        transaction: Transaction,
        items_data: list[TransactionItemDetail],
        transfer_type: str,
    ) -> None:
        print("transaction:", transaction)
        print("items_data:", items_data)
        self._start_worker(transaction, items_data, transfer_type)

    def _start_worker(
        self,
        transaction: Transaction,
        items_data: list[TransactionItemDetail],
        transfer_type: str,
    ) -> None:
        self.thread = QThread()
        self.worker = TransactionDocumentWorker(transaction, items_data, transfer_type)
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
        QTimer.singleShot(1000, lambda: self._finish_export(pdf_document=pdf_document))

    def _clean_thread(self) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()

    def _reset_variables(self) -> None:
        self.thread = None
        self.worker = None

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
        print("document ok:", pdf_document)

    @staticmethod
    def _handle_export_error(
        error: str, method: str, parent: QWidget, error_key: str = "DOCUMENT_ERROR"
    ) -> None:
        if not error:
            error = f"Unknown document error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", "export", "critical")
        ErrorDialog(parent).show_dialog(error_key, False)
