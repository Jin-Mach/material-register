from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QShowEvent, Qt
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from material_register.controllers.export_controllers.pdf.transaction_document_controller import (
    TransactionDocumentController,
)
from material_register.controllers.transactions_controller import TransactionsController
from material_register.db.models.transactions_models.transactions_proxy_model import (
    TransactionsProxyModel,
)
from material_register.init.data_init import DataInit
from material_register.services.error_handler import ErrorHandler
from material_register.services.search_manager import SearchManager
from material_register.ui.config.styles_constants import PRICE_STYLE
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    TRANSFER_IN,
    TRANSFER_OUT,
    UI_MARGINS_5,
    UI_SPACING,
)
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.transactions.transactions_widgets.transaction_detail_widget import (
    TransactionDetailWidget,
)
from material_register.ui.transactions.transactions_widgets.transactions_actions_widget import (
    TransactionsActionsWidget,
)
from material_register.ui.transactions.transactions_widgets.transactions_tab_widget import (
    TransactionsTabWidget,
)
from material_register.utils.formatting_utils import format_number_to_locale

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class TransactionsWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.stacked_widget = stacked_widget
        self.transactions_load_model_in = DataInit.transactions_load_model_in
        self.transactions_load_model_out = DataInit.transactions_load_model_out
        self.transactions_controller = TransactionsController(
            self, self.transactions_load_model_in, self.transactions_load_model_out
        )
        self.transaction_document_controller = TransactionDocumentController(
            self, self.transactions_load_model_in, self.transactions_load_model_out
        )
        SearchManager.setup_controllers(
            transactions_controller=self.transactions_controller
        )
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()
        self._apply_timer()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        main_layout.addWidget(self._create_actions_group(), 0)
        main_layout.addWidget(self._create_detail_group(), 0)
        main_layout.addWidget(self._create_transactions_group(), 1)
        main_layout.addWidget(self._create_count_group())
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_style()
        self._setup_model()
        self.transactions_controller.load_transactions()
        self.set_count_text(
            self.transactions_load_model_in.rowCount(),
            self.transactions_load_model_in.total_count,
        )
        self.transactions_controller.update_total_price()

    def _setup_texts(self) -> None:
        widgets = [self.detail_group_box, self.transactions_group_box]
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.model_in_suffix = ui_texts.get("modelInSuffix", "")
        self.items_count_text = ui_texts.get("itemsCountLabelText", "Count:")
        self.price_prefix = ui_texts.get("pricePrefix", "")
        self.price_sufix = ui_texts.get("priceSuffix", "")
        self.tooltip_texts = {
            "customer_text": ui_texts.get("tooltipCustomerText", "Customer:"),
            "address_text": ui_texts.get("tooltipAddressText", "Address:"),
            "payment_text": ui_texts.get("tooltipPaymentText", "Payment:"),
            "CASH": ui_texts.get("CASH", "Cash"),
            "TRANSFER": ui_texts.get("TRANSFER", "Transfer"),
            "notes_text": ui_texts.get("tooltipNotesText", "Notes:"),
        }
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.transactions_actions_widget.in_transaction_button.clicked.connect(
            lambda: self.transactions_controller.create_transaction(TRANSFER_IN)
        )
        self.transactions_actions_widget.out_transaction_button.clicked.connect(
            lambda: self.transactions_controller.create_transaction(TRANSFER_OUT)
        )
        self.transactions_actions_widget.base_filter_combobox.currentIndexChanged.connect(
            self._on_index_changed
        )
        self.transactions_tab_widget.currentChanged.connect(
            self.transactions_controller.reset_model_data
        )
        self.transactions_tab_widget.currentChanged.connect(self._on_tab_changed)
        self.transactions_actions_widget.search_line_edit.textChanged.connect(
            self._on_text_changed
        )
        self.transactions_tab_widget.transaction_in_view.selectionModel().currentChanged.connect(
            self.transactions_controller.update_transaction_detail_widget
        )
        self.transactions_tab_widget.transactions_out_view.selectionModel().currentChanged.connect(
            self.transactions_controller.update_transaction_detail_widget
        )

    def _create_actions_group(self) -> QGroupBox:
        self.transactions_actions_widget = TransactionsActionsWidget(self)
        group_box = QGroupBox()
        group_box.setObjectName("actionsGroupBox")
        layout = QHBoxLayout()
        layout.setContentsMargins(*UI_MARGINS_5)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.transactions_actions_widget)
        group_box.setLayout(layout)
        self.actions_group_box = group_box
        return group_box

    def _create_detail_group(self) -> QGroupBox:
        self.transaction_detail_widget = TransactionDetailWidget(self)
        group_box = QGroupBox()
        group_box.setObjectName("detailGroupBox")
        layout = QVBoxLayout()
        layout.setContentsMargins(*UI_MARGINS_5)
        layout.addWidget(self.transaction_detail_widget)
        group_box.setLayout(layout)
        self.detail_group_box = group_box
        return group_box

    def _create_transactions_group(self) -> QGroupBox:
        self.transactions_tab_widget = TransactionsTabWidget(self)
        group_box = QGroupBox()
        group_box.setObjectName("transactionsGroupBox")
        layout = QVBoxLayout()
        layout.setContentsMargins(*UI_MARGINS_5)
        layout.addSpacing(5)
        layout.addWidget(self.transactions_tab_widget)
        group_box.setLayout(layout)
        self.transactions_group_box = group_box
        return group_box

    def _create_count_group(self) -> QGroupBox:
        group_box = QGroupBox()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        self.items_count_label = QLabel()
        self.items_count_label.setObjectName("itemsCountLabel")
        self.price_count_label = QLabel()
        self.price_count_label.setObjectName("priceCountLabel")
        self.price_count_value = QLabel()
        self.price_count_value.setObjectName("priceCountValue")
        layout.addWidget(self.items_count_label)
        layout.addStretch()
        layout.addWidget(self.price_count_label)
        layout.addWidget(self.price_count_value)
        group_box.setLayout(layout)
        return group_box

    def _setup_style(self) -> None:
        font = QFont()
        font.setBold(True)
        self.price_count_value.setStyleSheet(PRICE_STYLE)
        self.price_count_value.setFont(font)

    def _setup_model(self) -> None:
        self._setup_in_model()
        self._setup_out_model()
        self.active_proxy = self.transactions_proxy_model_in

    def _setup_in_model(self) -> None:
        self.transactions_proxy_model_in = TransactionsProxyModel()
        self.transactions_proxy_model_in.setSourceModel(self.transactions_load_model_in)
        self.transactions_tab_widget.transaction_in_view.setModel(
            self.transactions_proxy_model_in
        )
        self.transactions_tab_widget.transaction_in_view.setup_ui()
        self.transactions_load_model_in.set_suffix(self.model_in_suffix)
        self.transactions_load_model_in.set_tooltip_texts(self.tooltip_texts)
        self.transactions_tab_widget.transaction_in_view.customContextMenuRequested.connect(
            self.transactions_tab_widget.transaction_in_view.open_context_menu
        )

    def _setup_out_model(self) -> None:
        self.transactions_proxy_model_out = TransactionsProxyModel()
        self.transactions_proxy_model_out.setSourceModel(
            self.transactions_load_model_out
        )
        self.transactions_tab_widget.transactions_out_view.setModel(
            self.transactions_proxy_model_out
        )
        self.transactions_tab_widget.transactions_out_view.setup_ui()
        self.transactions_load_model_out.set_tooltip_texts(self.tooltip_texts)
        self.transactions_tab_widget.transactions_out_view.customContextMenuRequested.connect(
            self.transactions_tab_widget.transactions_out_view.open_context_menu
        )

    def _apply_timer(self) -> None:
        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.setInterval(300)
        self.filter_timer.timeout.connect(self._apply_filter)

    def _on_tab_changed(self, index: int) -> None:
        if index == 0:
            self.active_proxy = self.transactions_proxy_model_in
        else:
            self.active_proxy = self.transactions_proxy_model_out

    def _on_index_changed(self) -> None:
        key = self.transactions_actions_widget.get_filter_key()
        if key:
            self.transactions_controller.set_basic_transactions_filter(key)

    def _on_text_changed(self) -> None:
        self.filter_timer.start()

    def _apply_filter(self) -> None:
        text = self.transactions_actions_widget.search_line_edit.text()
        self.transactions_controller.set_proxy_transactions_filter(text)

    def set_count_text(self, filtered: int, total: int) -> None:
        self.items_count_label.setText(f"{self.items_count_text} {filtered}/{total}")

    def set_price_text(self, total_price: float) -> None:
        filter_text = (
            self.transactions_actions_widget.base_filter_combobox.currentText()
        )
        self.price_count_label.setText(f"{self.price_prefix} ({filter_text.lower()}):")
        self.price_count_value.setText(
            f"{format_number_to_locale(total_price)} {self.price_sufix}"
        )

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.setFocus()
