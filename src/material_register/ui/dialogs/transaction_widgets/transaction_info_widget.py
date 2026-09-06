from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from material_register.config.ui_constants import (
    TRANSACTION_INFO_WIDGET_NOTES_LENGTH,
    TRANSFER_OUT,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.notes_length_handler import check_notes_length
from material_register.ui.helpers.styles import WARNING_STYLE
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.setup.ui_widgets import setup_text_edit

if TYPE_CHECKING:
    from material_register.ui.dialogs.transaction_items_dialog_in import (
        TransactionItemsDialogIn,
    )
    from material_register.ui.dialogs.transaction_items_dialog_out import (
        TransactionItemsDialogOut,
    )


class TransactionInfoWidget(QWidget):
    def __init__(
        self,
        transaction_item_dialog: "TransactionItemsDialogIn | TransactionItemsDialogOut",
        transfer_type: str,
    ) -> None:
        super().__init__(transaction_item_dialog)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.transfer_type = transfer_type
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        self.payment_info = QLabel()
        self.payment_info.setObjectName("paymentInfo")
        self.payment_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        customer_notes_layout = QHBoxLayout()
        self.customer_group_box = QGroupBox()
        self.customer_group_box.setObjectName("customerGroupBox")
        self.customer_group_box.setMinimumWidth(300)
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(5)
        customer_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        customer_form_layout = QFormLayout()
        customer_form_layout.setFormAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.customer_name_label = QLabel()
        self.customer_name_label.setObjectName("customerNameLabel")
        self.customer_name = QLabel()
        self.customer_name.setObjectName("customerName")
        self.document_number_label = QLabel()
        self.document_number_label.setObjectName("documentNumberLabel")
        self.document_number = QLabel()
        self.document_number.setObjectName("documentNumber")
        self.address_label = QLabel()
        self.address_label.setObjectName("addressLabel")
        self.address_label.setWordWrap(True)
        self.address = QLabel()
        self.address.setObjectName("address")
        button_layout = QHBoxLayout()
        self.update_transaction_info_button = QPushButton()
        self.update_transaction_info_button.setObjectName("updateTransactionInfoButton")
        self.notes_group_box = QGroupBox()
        self.notes_group_box.setObjectName("notesGroupBox")
        self.notes_group_box.setMinimumWidth(200)
        notes_layout = QVBoxLayout()
        self.notes_edit = QTextEdit()
        count_layout = QHBoxLayout()
        self.notes_count_label = QLabel()
        self.notes_count_label.setObjectName("notesCountLabel")
        customer_form_layout.addRow(self.customer_name_label, self.customer_name)
        customer_form_layout.addRow(self.document_number_label, self.document_number)
        customer_form_layout.addRow(self.address_label, self.address)
        button_layout.addStretch()
        button_layout.addWidget(self.update_transaction_info_button)
        customer_layout.addLayout(customer_form_layout)
        customer_layout.addLayout(button_layout)
        self.customer_group_box.setLayout(customer_layout)
        count_layout.addWidget(self.notes_count_label)
        count_layout.addStretch()
        notes_layout.addWidget(self.notes_edit)
        notes_layout.addLayout(count_layout)
        self.notes_group_box.setLayout(notes_layout)
        customer_notes_layout.addWidget(self.customer_group_box)
        customer_notes_layout.addWidget(self.notes_group_box, 3)
        main_layout.addWidget(self.payment_info)
        main_layout.addLayout(customer_notes_layout)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_text_edit()
        self._setup_style()
        self._update_notes_count()

    def _setup_texts(self) -> None:
        widgets = [
            self.customer_group_box,
            self.customer_name_label,
            self.document_number_label,
            self.address_label,
            self.notes_group_box,
            self.notes_count_label,
            self.update_transaction_info_button,
        ]
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.notes_count_text = ui_texts.get(
            f"{self.notes_count_label.objectName()}Text", "Count:"
        )
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_text_edit(self) -> None:
        setup_text_edit(self.notes_edit)

    def _setup_style(self) -> None:
        font = QFont()
        font.setBold(True)
        self.payment_info.setFont(font)
        self.payment_info.setStyleSheet(WARNING_STYLE)

    def _create_connection(self) -> None:
        self.notes_edit.textChanged.connect(self._update_notes_count)

    def _update_notes_count(self) -> None:
        check_notes_length(
            self.notes_edit,
            self.notes_count_label,
            self.notes_count_text,
            TRANSACTION_INFO_WIDGET_NOTES_LENGTH,
        )

    def _apply_transfer_type(self, payment_text: str) -> None:
        if self.transfer_type == TRANSFER_OUT:
            self.payment_info.hide()
        self.payment_info.setText(payment_text)

    def set_create_data(
        self,
        payment_text: str,
        customer: str,
        document_number: str,
        address: str,
        notes: str,
    ) -> None:
        self._apply_transfer_type(payment_text)
        self.customer_name.setText(customer)
        self.document_number.setText(document_number)
        self.address.setText(address)
        self.notes_edit.setPlainText(notes)

    def get_notes(self) -> str:
        return self.notes_edit.toPlainText().strip()
