from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QSize, QStandardPaths
from PySide6.QtGui import QShowEvent
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from material_register.controllers.documents_controller import DocumentsController
from material_register.providers.settings_provider import SettingsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.window_positioning import centre_dialog
from material_register.ui.setup.ui_icons import UiIcons
from material_register.ui.setup.ui_texts import UiTexts


class DocumentPreviewDialog(QDialog):
    MIN_ZOOM_FACTOR = 0.5
    MAX_ZOOM_FACTOR = 2.0

    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(400, 500)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()
        self.settings = SettingsProvider.SETTINGS.get("export", {}).get("documents", {})
        self._current_zoom = 1.0
        self._pdf_bytes = None
        self._pdf_file_name = None

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
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self._pdf_default_name = ui_texts.get("pdfDefaultName", "Document")
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
        self.zoom_in_button.clicked.connect(self._zoom_in)
        self.zoom_reset_button.clicked.connect(self._reset_zoom)
        self.zoom_out_button.clicked.connect(self._zoom_out)
        self.close_button.clicked.connect(self.close)

    def load_pdf_from_bytes(self, pdf_bytes: bytes, transaction_id: int) -> None:
        self._pdf_bytes = pdf_bytes
        self._pdf_file_name = f"{self._pdf_default_name}_{transaction_id:06d}.pdf"
        self.pdf_buffer.setData(QByteArray(pdf_bytes))
        self.pdf_buffer.open(QBuffer.OpenModeFlag.ReadOnly)
        self.pdf_document.load(self.pdf_buffer)
        self.pdf_view.setDocument(self.pdf_document)
        self._current_zoom = self._get_fit_in_view_zoom()

    def _print_document(self) -> None:
        printer_name = self.settings.get("user", {}).get("printerNameLineEdit", "")
        if not printer_name:
            return
        print("Print")

    def _save_document(self) -> None:
        path = self.settings.get("user", {}).get("savePathLineEdit", "")
        if not path:
            path = QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.DocumentsLocation
            )
        path = Path(path) / self._pdf_file_name
        DocumentsController.save_pdf_document(self._pdf_bytes, path, self)

    def _zoom_in(self) -> None:
        if self.pdf_view.zoomMode() != QPdfView.ZoomMode.Custom:
            self._current_zoom = self._get_fit_in_view_zoom()
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self._current_zoom = min(self._current_zoom * 1.1, self.MAX_ZOOM_FACTOR)
        self.pdf_view.setZoomFactor(self._current_zoom)

    def _reset_zoom(self) -> None:
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitInView)
        self._current_zoom = self._get_fit_in_view_zoom()

    def _zoom_out(self) -> None:
        if self.pdf_view.zoomMode() != QPdfView.ZoomMode.Custom:
            self._current_zoom = self._get_fit_in_view_zoom()
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.Custom)
        self._current_zoom = max(self._current_zoom / 1.1, self.MIN_ZOOM_FACTOR)
        self.pdf_view.setZoomFactor(self._current_zoom)

    def _get_fit_in_view_zoom(self) -> float:
        if not self.pdf_document or self.pdf_document.pageCount() == 0:
            return 1.0
        page_size_points = self.pdf_document.pagePointSize(0)
        dpi = QApplication.primaryScreen().logicalDotsPerInch()
        page_width = (page_size_points.width() / 72.0) * dpi
        page_height = (page_size_points.height() / 72.0) * dpi
        view_width = self.pdf_view.viewport().width()
        view_height = self.pdf_view.viewport().height()
        if page_width <= 0 or page_height <= 0:
            return 1.0
        scale_width = view_width / page_width
        scale_height = view_height / page_height
        return min(scale_width, scale_height)

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
        self._current_zoom = self._get_fit_in_view_zoom()
