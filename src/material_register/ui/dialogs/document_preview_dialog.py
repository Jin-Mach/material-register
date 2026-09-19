from PySide6.QtGui import QShowEvent
from PySide6.QtCore import QBuffer, QByteArray, QSize
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget, QApplication
)

from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_icons import UiIcons
from material_register.ui.setup.ui_texts import UiTexts


class DocumentPreviewDialog(QDialog):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(400, 500)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(5)
        self.print_document_button = QPushButton()
        self.print_document_button.setObjectName("printDocumentButton")
        self.save_document_button = QPushButton()
        self.save_document_button.setObjectName("saveDocumentButton")
        self.zoom_in_button = QPushButton()
        self.zoom_in_button.setObjectName("zoomInButton")
        self.zoom_reset_button = QPushButton()
        self.zoom_reset_button.setObjectName("zoomResetButton")
        self.zoom_out_button = QPushButton()
        self.zoom_out_button.setObjectName("zoomOutButton")
        self.pdf_view = QPdfView()
        self.pdf_view.setObjectName("pdfView")
        self.pdf_document = QPdfDocument()
        self.pdf_buffer = QBuffer()
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.close_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.close_button.setObjectName("closeButton")
        buttons_layout.addWidget(self.print_document_button)
        buttons_layout.addWidget(self.save_document_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.zoom_in_button)
        buttons_layout.addWidget(self.zoom_reset_button)
        buttons_layout.addWidget(self.zoom_out_button)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.pdf_view)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_view()
        self._setup_icons()

    def _setup_texts(self) -> None:
        buttons = self.findChildren(QPushButton)
        if UiTexts.set_ui_texts(self, buttons):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, buttons):
            return

    def _setup_view(self) -> None:
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
        self.pdf_view.setPageSpacing(10)

    def _setup_icons(self) -> None:
        self.print_document_button.setIcon(UiIcons.PRINT_ICON)
        self.save_document_button.setIcon(UiIcons.SAVE_ICON)
        self.zoom_in_button.setIcon(UiIcons.ZOOM_IN_ICON)
        self.zoom_reset_button.setIcon(UiIcons.ZOOM_RESET_ICON)
        self.zoom_out_button.setIcon(UiIcons.ZOOM_OUT_ICON)
        buttons = [
            self.print_document_button,
            self.save_document_button,
            self.zoom_in_button,
            self.zoom_reset_button,
            self.zoom_out_button,
        ]
        for button in buttons:
            button.setIconSize(QSize(24, 24))
            button.setFixedSize(28, 28)

    def _create_connection(self) -> None:
        self.print_document_button.clicked.connect(self._print_document)
        self.save_document_button.clicked.connect(self._save_document)
        self.close_button.clicked.connect(self.close)

    def load_pdf_from_bytes(self, pdf_document: bytes) -> None:
        self.pdf_buffer.setData(QByteArray(pdf_document))
        self.pdf_buffer.open(QBuffer.OpenModeFlag.ReadOnly)
        self.pdf_document.load(self.pdf_buffer)
        self.pdf_view.setDocument(self.pdf_document)

    def _print_document(self) -> None:
        print("Print")

    def _save_document(self) -> None:
        print("Save")

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        screen = QApplication.primaryScreen()
        available_geometry = screen.availableGeometry()
        dpi = screen.logicalDotsPerInch()
        a4_height = int((297 / 25.4) * dpi)
        height = min(int(available_geometry.height() * 0.9), a4_height)
        width = int(height * 210 / 297)
        self.setFixedSize(width, height)
        centre_dialog(self)
