from PySide6.QtCore import QObject, Signal, Slot

from material_register.domain.branch_dataclass import BranchDataclass
from material_register.domain.transaction_dataclass import Transaction
from material_register.domain.transaction_item_detail_dataclass import (
    TransactionItemDetail,
)
from material_register.services.error_handler import ErrorHandler
from material_register.services.export.pdf.documents.transaction_document_in import (
    TransactionDocumentIn,
)
from material_register.services.export.pdf.documents.transaction_document_out import (
    TransactionDocumentOut,
)
from material_register.ui.config.ui_constants import TRANSFER_IN, TRANSFER_OUT


class TransactionDocumentWorker(QObject):
    finished = Signal(bytes)
    error = Signal(str)

    def __init__(
        self,
        transaction: Transaction,
        items_data: list[TransactionItemDetail],
        transfer_type: str,
        branch_settings: BranchDataclass,
        export_texts: dict[str, dict[str, str]],
    ) -> None:
        super().__init__()
        self.transaction = transaction
        self.items_data = items_data
        self.transfer_type = transfer_type
        self.branch_settings = branch_settings
        self.export_texts = export_texts

    @Slot()
    def run(self) -> None:
        try:
            pdf_document = None
            if self.transfer_type == TRANSFER_IN:
                pdf_document = TransactionDocumentIn.create_document(
                    self.transaction,
                    self.items_data,
                    self.branch_settings,
                    self.export_texts,
                )
            elif self.transfer_type == TRANSFER_OUT:
                pdf_document = TransactionDocumentOut.create_document(
                    self.transaction,
                    self.items_data,
                    self.branch_settings,
                    self.export_texts,
                )
            if not pdf_document:
                self.error.emit("PDF_FAILED")
                return
            self.finished.emit(pdf_document)
        except Exception as e:
            ErrorHandler.handle_error(e, "export", "error")
            self.error.emit(f"Document failed: {e}")
