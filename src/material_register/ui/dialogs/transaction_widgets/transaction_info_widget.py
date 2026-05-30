from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit,
                               QSizePolicy, QFrame)

if TYPE_CHECKING:
    from material_register.ui.dialogs.transaction_items_dialog import TransactionItemsDialog


class TransactionInfoWidget(QWidget):
    def __init__(self, transaction_item_dialog: "TransactionItemsDialog") -> None:
        super().__init__(transaction_item_dialog)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setLayout(self._create_ui())

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        type_layout = QHBoxLayout()
        type_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.transaction_info = QLabel("In | Cash")
        customer_frame = QFrame()
        customer_frame.setFrameShape(QFrame.Shape.StyledPanel)
        customer_layout = QVBoxLayout()
        info_layout = QFormLayout()
        self.customer_name_label = QLabel("Customer:")
        self.customer_name_label.setObjectName("customerNameLabel")
        self.customer_name = QLabel("xxx")
        self.document_number_label = QLabel("Document:")
        self.document_number_label.setObjectName("documentNumberLabel")
        self.document_number = QLabel("123")
        self.address_label = QLabel("Address:")
        self.address_label.setObjectName("addressLabel")
        self.address = QLabel("yyyyy")
        button_layout = QHBoxLayout()
        self.update_transaction_info_button = QPushButton("Update")
        self.update_transaction_info_button.setObjectName("updateTransactionInfoButton")
        notes_layout = QVBoxLayout()
        self.notes = QTextEdit()
        count_layout = QHBoxLayout()
        self.notes_count_label = QLabel("Notes: 10/20")
        type_layout.addWidget(self.transaction_info)
        info_layout.addRow(self.customer_name_label, self.customer_name)
        info_layout.addRow(self.document_number_label, self.document_number)
        info_layout.addRow(self.address_label, self.address)
        button_layout.addStretch()
        button_layout.addWidget(self.update_transaction_info_button)
        customer_layout.addLayout(type_layout)
        customer_layout.addLayout(info_layout)
        customer_layout.addLayout(button_layout)
        count_layout.addWidget(self.notes_count_label)
        count_layout.addStretch()
        notes_layout.addWidget(self.notes)
        notes_layout.addLayout(count_layout)
        customer_frame.setLayout(customer_layout)
        main_layout.addWidget(customer_frame)
        main_layout.addLayout(notes_layout, 3)
        return main_layout