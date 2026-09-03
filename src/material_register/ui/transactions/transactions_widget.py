from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont, QShowEvent
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from material_register.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.controllers.transactions_controller import TransactionsController
from material_register.db.models.transactions_proxy_filter import (
    TransactionsProxyFilter,
)
from material_register.init.data_init import DataInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.formating_utils import format_number_to_locale
from material_register.ui.helpers.styles import PRICE_STYLE
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.transactions.transactions_widgets.transactions_actions_widget import (
    TransactionsActionsWidget,
)
from material_register.ui.transactions.transactions_widgets.transactions_tab_widget import (
    TransactionsTabWidget,
)

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
        self.setLayout(self.create_ui())
        self._setup_ui()
        self._create_connection()
        self._apply_timer()

    def create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        self.transactions_actions_widget = TransactionsActionsWidget(self)
        self.transactions_tab_widget = TransactionsTabWidget(self)
        count_group_box = QGroupBox()
        count_layout = QHBoxLayout()
        count_layout.setSpacing(0)
        self.items_count_label = QLabel()
        self.items_count_label.setObjectName("itemsCountLabel")
        self.price_count_label = QLabel()
        self.price_count_label.setObjectName("priceCountLabel")
        self.price_count_value = QLabel()
        self.price_count_value.setObjectName("priceCountValue")
        count_layout.addWidget(self.items_count_label)
        count_layout.addStretch()
        count_layout.addWidget(self.price_count_label)
        count_layout.addWidget(self.price_count_value)
        count_group_box.setLayout(count_layout)
        main_layout.addWidget(self.transactions_actions_widget)
        main_layout.addWidget(self.transactions_tab_widget)
        main_layout.addWidget(count_group_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_style()
        self._setup_model()
        self.set_count_text(
            self.transactions_load_model_in.rowCount(),
            self.transactions_load_model_in.total_count,
        )
        self.transactions_controller.update_total_price()

    def _setup_texts(self) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            ErrorHandler.handle_error(
                f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.model_in_suffix = ui_texts.get("modelInSuffix", "")
        self.items_count_text = ui_texts.get("itemsCountLabelText", "Count:")
        self.price_prefix = ui_texts.get("pricePrefix", "")
        self.price_sufix = ui_texts.get("priceSuffix", "")

    def _setup_style(self) -> None:
        font = QFont()
        font.setBold(True)
        self.price_count_value.setStyleSheet(PRICE_STYLE)
        self.price_count_value.setFont(font)

    def _setup_model(self) -> None:
        self._setup_in_model()
        self._setup_out_model()
        self.active_proxy = self.transactions_proxy_filter_in

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

    def _setup_in_model(self) -> None:
        self.transactions_proxy_filter_in = TransactionsProxyFilter()
        self.transactions_proxy_filter_in.setSourceModel(
            self.transactions_load_model_in
        )
        self.transactions_tab_widget.transaction_in_view.setModel(
            self.transactions_proxy_filter_in
        )
        self.transactions_tab_widget.transaction_in_view.setup_texts()
        self.transactions_load_model_in.set_suffix(self.model_in_suffix)
        self.transactions_load_model_in.load_transactions_data()
        self.transactions_tab_widget.transaction_in_view.customContextMenuRequested.connect(
            self.transactions_tab_widget.transaction_in_view.open_context_menu
        )

    def _setup_out_model(self) -> None:
        self.transactions_proxy_filter_out = TransactionsProxyFilter()
        self.transactions_proxy_filter_out.setSourceModel(
            self.transactions_load_model_out
        )
        self.transactions_tab_widget.transactions_out_view.setModel(
            self.transactions_proxy_filter_out
        )
        self.transactions_tab_widget.transactions_out_view.setup_texts()
        self.transactions_load_model_out.load_transactions_data()
        self.transactions_tab_widget.transactions_out_view.customContextMenuRequested.connect(
            self.transactions_tab_widget.transactions_out_view.open_context_menu
        )

    def _on_tab_changed(self, index: int) -> None:
        if index == 0:
            self.active_proxy = self.transactions_proxy_filter_in
        else:
            self.active_proxy = self.transactions_proxy_filter_out

    def _on_index_changed(self) -> None:
        key = self.transactions_actions_widget.get_filter_key()
        if key:
            self.transactions_controller.set_basic_transactions_filter(key)

    def _on_text_changed(self) -> None:
        self.filter_timer.start()

    def _apply_filter(self) -> None:
        text = self.transactions_actions_widget.search_line_edit.text()
        self.transactions_controller.set_proxy_transactions_filter(text)

    def _apply_timer(self) -> None:
        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.setInterval(300)
        self.filter_timer.timeout.connect(self._apply_filter)

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
