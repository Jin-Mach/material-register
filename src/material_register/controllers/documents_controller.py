from pathlib import Path

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtGui import QPainter
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter, QPrinterInfo
from PySide6.QtWidgets import QWidget

from material_register.core.app_context import AppContext
from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_EXPORT,
)
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
                e, f"{DocumentsController.__name__}.save_pdf_document", parent
            )

    @staticmethod
    def print_document(
        pdf_document: QPdfDocument, printer_name: str, parent: QWidget
    ) -> None:
        printer_info = QPrinterInfo.printerInfo(printer_name)

        if not printer_name or printer_info.isNull():
            printer = QPrinter()
            dialog = QPrintDialog(printer, parent)
            if dialog.exec() != QPrintDialog.DialogCode.Accepted:
                return
            printer_name = printer.printerName()
            printer_info = QPrinterInfo.printerInfo(printer_name)
            if not printer_name or printer_info.isNull():
                return
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPrinterName(printer_name)
        if printer.printerState() == QPrinter.PrinterState.Error:
            printer = QPrinter()
            dialog = QPrintDialog(printer, parent)
            if dialog.exec() != QPrintDialog.DialogCode.Accepted:
                return
            printer_name = printer.printerName()
            if not printer_name:
                return
        DocumentsController._print_pdf_document(pdf_document, printer_name, parent)

    @staticmethod
    def _print_pdf_document(
        pdf_document: QPdfDocument, printer_name: str, parent: QWidget
    ) -> None:
        painter = None
        try:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setPrinterName(printer_name)
            printer_resolution = printer.resolution()
            printer_rectangle = printer.pageRect(QPrinter.Unit.DevicePixel)
            page_count = pdf_document.pageCount()
            painter = QPainter()
            if not painter.begin(printer):
                raise RuntimeError("Could not initialize printer painter")
            for page in range(page_count):
                page_size = pdf_document.pagePointSize(page)
                image_size = QSize(
                    round(page_size.width() / 72 * printer_resolution),
                    round(page_size.height() / 72 * printer_resolution),
                )
                image = pdf_document.render(page, image_size)
                scaled_size = image_size.scaled(
                    printer_rectangle.size().toSize(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                )
                target_rectangle = QRect(
                    QPoint(printer_rectangle.x(), printer_rectangle.y()),
                    scaled_size,
                )
                target_rectangle.moveCenter(printer_rectangle.center().toPoint())
                painter.drawImage(target_rectangle, image)
                if page < page_count - 1:
                    printer.newPage()
            notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("DOCUMENTS", None)
            if notification_texts:
                DocumentsController._notification_handler(
                    notification_texts,
                    "DOCUMENT_SENT",
                    "Document sent to print queue",
                )
        except Exception as e:
            DocumentsController._handle_documents_error(
                e,
                f"{DocumentsController.__name__}.print_pdf_document",
                parent,
            )
        finally:
            if painter.isActive():
                painter.end()

    @staticmethod
    def _handle_documents_error(error: Exception, method: str, parent: QWidget) -> None:
        ErrorHandler.handle_error(
            f"{error}: {method}", LOGGER_EXPORT, LOG_LEVEL_WARNING
        )
        ErrorDialog(parent).show_dialog("DOCUMENT_ERROR", False)

    @staticmethod
    def _notification_handler(
        notification_texts: dict[str, str], key: str, default: str
    ) -> None:
        notification = NotificationDialog(
            AppContext.MAIN_WINDOW, notification_texts.get(key, default)
        )
        notification.show_notification()
