from PySide6.QtCore import QBuffer, QByteArray
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class DocumentPreviewDialog(QDialog):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setLayout(self._create_ui())
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        buttons_layout = QHBoxLayout()
        self.print_button = QPushButton("Print")
        self.print_button.setObjectName("printButton")
        self.save_button = QPushButton("Save")
        self.save_button.setObjectName("saveButton")
        self.pdf_view = QPdfView()
        self.pdf_view.setObjectName("pdfView")
        self.pdf_document = QPdfDocument()
        self.pdf_buffer = QBuffer()
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        self.close_button = button_box.button(QDialogButtonBox.StandardButton.Close)
        self.close_button.setObjectName("closeButton")
        buttons_layout.addWidget(self.print_button)
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.pdf_view)
        main_layout.addWidget(button_box)
        return main_layout

    def _create_connection(self) -> None:
        self.print_button.clicked.connect(self._print_document)
        self.save_button.clicked.connect(self._save_document)
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
