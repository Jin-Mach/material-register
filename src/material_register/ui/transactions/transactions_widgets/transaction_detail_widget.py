from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QShowEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from material_register.db.models.transaction_items_model_in import (
    TransactionItemsModelIn,
)
from material_register.db.models.transaction_items_model_out import (
    TransactionItemsModelOut,
)
from material_register.domain.transaction_item_detail_dataclass import (
    TransactionItemDetail,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.styles_constants import WARNING_STYLE
from material_register.ui.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.transactions.transactions_widgets.transaction_detail_view import (
    TransactionDetailView,
)

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


class TransactionDetailWidget(QWidget):
    def __init__(self, transaction_widget: "TransactionsWidget") -> None:
        super().__init__(transaction_widget)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self.items_model = None

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.tab_widget = QTabWidget()
        self.info_tab = self._create_info_tab()
        self.items_tab = self._create_items_tab()
        self.tab_widget.addTab(self.info_tab, "")
        self.tab_widget.addTab(self.items_tab, "")
        main_layout.addWidget(self.tab_widget)
        return main_layout

    def _create_info_tab(self) -> QWidget:
        info_tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)
        payment_layout = QHBoxLayout()
        payment_layout.setContentsMargins(0, 0, 0, 0)
        self.payment_info = QLabel()
        self.payment_info.setObjectName("paymentInfo")
        self.payment_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.is_invoiced_checkbox = QCheckBox()
        self.is_invoiced_checkbox.setObjectName("isInvoicedCheckBox")
        payment_layout.addStretch()
        payment_layout.addWidget(self.payment_info)
        payment_layout.addSpacing(20)
        payment_layout.addWidget(self.is_invoiced_checkbox)
        payment_layout.addStretch()
        info_content_layout = QHBoxLayout()
        info_content_layout.setSpacing(5)
        customer_section = self._create_customer_section()
        notes_section = self._create_notes_section()
        info_content_layout.addWidget(customer_section)
        info_content_layout.addWidget(notes_section, 1)
        main_layout.addLayout(payment_layout)
        main_layout.addLayout(info_content_layout, 1)
        info_tab.setLayout(main_layout)
        return info_tab

    def _create_customer_section(self) -> QGroupBox:
        self.customer_group_box = QGroupBox()
        self.customer_group_box.setObjectName("customerGroupBox")
        self.customer_group_box.setFixedWidth(400)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        form_layout = QFormLayout()
        form_layout.setFormAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.customer_name_label = QLabel()
        self.customer_name_label.setObjectName("customerNameLabel")
        self.customer_name = QLabel()
        self.document_number_label = QLabel()
        self.document_number_label.setObjectName("documentNumberLabel")
        self.customer_document = QLabel()
        self.customer_address_label = QLabel()
        self.customer_address_label.setObjectName("addressLabel")
        self.address_label = QLabel()
        form_layout.addRow(self.customer_name_label, self.customer_name)
        form_layout.addRow(self.document_number_label, self.customer_document)
        form_layout.addRow(self.customer_address_label, self.address_label)
        main_layout.addLayout(form_layout)
        self.customer_group_box.setLayout(main_layout)
        return self.customer_group_box

    def _create_notes_section(self) -> QGroupBox:
        self.notes_group_box = QGroupBox()
        self.notes_group_box.setObjectName("notesGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        self.notes_label = QLabel()
        self.notes_label.setObjectName("notesLabel")
        self.notes_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        self.notes_label.setWordWrap(True)
        main_layout.addWidget(self.notes_label)
        self.notes_group_box.setLayout(main_layout)
        return self.notes_group_box

    def _create_items_tab(self) -> QWidget:
        items_tab = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.detail_view = TransactionDetailView(self)
        main_layout.addWidget(self.detail_view)
        items_tab.setLayout(main_layout)
        return items_tab

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_check_box()
        self._setup_style()

    def _setup_texts(self) -> None:
        widgets = [
            self.is_invoiced_checkbox,
            self.customer_group_box,
            self.customer_name_label,
            self.document_number_label,
            self.customer_address_label,
            self.notes_group_box,
        ]
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.info_tab_text = ui_texts.get("infoTabText", "")
        self.items_tab_text = ui_texts.get("itemsTabText", "")
        self.cash_payment = ui_texts.get("CASH", "CASH")
        self.transfer_payment = ui_texts.get("TRANSFER", "TRANSFER")
        self.price_suffix = ui_texts.get("priceSuffix", "")
        self.tab_widget.setTabText(0, self.info_tab_text)
        self.tab_widget.setTabText(1, self.items_tab_text)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_check_box(self) -> None:
        self.is_invoiced_checkbox.setDisabled(True)
        self.is_invoiced_checkbox.hide()

    def _setup_style(self) -> None:
        font = QFont()
        font.setBold(True)
        self.payment_info.setFont(font)
        self.payment_info.setStyleSheet(WARNING_STYLE)

    def _apply_payment_data(self, create_data: dict[str, str | int]) -> None:
        self.payment_info.show()
        payment_type = create_data.get("paymentType", "N/A")
        if payment_type == "CASH":
            self.payment_info.setText(self.cash_payment)
            self.is_invoiced_checkbox.hide()
        elif payment_type == "TRANSFER":
            self.payment_info.setText(self.transfer_payment)
            self.is_invoiced_checkbox.show()
        else:
            self.payment_info.clear()
            self.is_invoiced_checkbox.hide()
        self.is_invoiced_checkbox.setChecked(bool(create_data.get("isInvoiced", False)))

    def _setup_customer_data(
        self,
        create_data: dict[str, str | int],
    ) -> None:
        self.customer_name.setText(str(create_data.get("customer", "")))
        self.customer_document.setText(str(create_data.get("documentNumber", "")))
        self.address_label.setText(str(create_data.get("address", "")))
        self.notes_label.setText(str(create_data.get("notes", "")))
        self.customer_group_box.layout().activate()

    def update_data(
        self,
        create_data: dict[str, str | int],
        items_data: list[TransactionItemDetail],
        transaction_type: str,
    ) -> None:
        if transaction_type == TRANSFER_IN:
            self.items_model = TransactionItemsModelIn(self.price_suffix)
        elif transaction_type == TRANSFER_OUT:
            self.items_model = TransactionItemsModelOut()
        self.detail_view.setModel(self.items_model)
        self.detail_view.setup_ui()
        for item in items_data:
            self.items_model.add_item(
                {
                    "category": item.category_name,
                    "commodity": item.commodity_name,
                    "commoditySuffix": item.commodity_suffix,
                    "commodityId": item.commodity_id,
                    "unitCount": item.unit_count,
                    "pricePerUnit": item.price_per_unit,
                }
            )
        self._setup_customer_data(create_data)
        if transaction_type == TRANSFER_OUT:
            self.payment_info.hide()
            self.is_invoiced_checkbox.hide()
        else:
            self._apply_payment_data(create_data)

    def reset_data(self) -> None:
        self.detail_view.setModel(None)
        self.items_model = None
        self.customer_name.clear()
        self.customer_document.clear()
        self.address_label.clear()
        self.notes_label.clear()
        self.payment_info.clear()
        self.is_invoiced_checkbox.setChecked(False)
        self.payment_info.hide()
        self.is_invoiced_checkbox.hide()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.setFixedHeight(self.height())
