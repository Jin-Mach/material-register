from pathlib import Path

from PySide6.QtWidgets import QWidget

from material_register.core.app_context import AppContext
from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.notification_dialog import NotificationDialog


class DocumentsController:
    @staticmethod
    def save_pdf_document(pdf_bytes: bytes, path: Path, parent: QWidget) -> None:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(pdf_bytes)
            notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("DOCUMENTS", None)
            if notification_texts:
                DocumentsController._notification_handler(
                    notification_texts, "DOCUMENT_SAVED", "Document saved"
                )
        except Exception as e:
            DocumentsController._handle_documents_error(
                e, f"{DocumentsController.__class__.__name__}.save_pdf_document", parent
            )

    @staticmethod
    def _handle_documents_error(error: Exception, method: str, parent: QWidget) -> None:
        ErrorHandler.handle_error(f"{error}: {method}", "export", "warning")
        ErrorDialog(parent).show_dialog("DOCUMENT_ERROR", False)

    @staticmethod
    def _notification_handler(
        notification_texts: dict[str, str], key: str, default: str
    ) -> None:
        notification = NotificationDialog(
            AppContext.MAIN_WINDOW, notification_texts.get(key, default)
        )
        notification.show_notification()
