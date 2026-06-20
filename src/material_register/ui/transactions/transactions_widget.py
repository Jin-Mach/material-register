from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from material_register.config.app_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.controllers.transactions_controller import TransactionsController
from material_register.init.data_init import DataInit
from material_register.init.db_init import DbInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.transactions.transactions_widgets.transactions_tab_widget import TransactionsTabWidget
from material_register.ui.transactions.transactions_widgets.transactions_actions_widget import TransactionsActionsWidget

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class TransactionsWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.stacked_widget = stacked_widget
        self.db_connection = DbInit.db_connection
        self.transactions_load_model_in = DataInit.transactions_load_model_in
        self.transactions_load_model_out = DataInit.transactions_load_model_out
        self.transactions_controller = TransactionsController(self, self.db_connection,
                                                              self.transactions_load_model_in,
                                                              self.transactions_load_model_out)
        self.setLayout(self.create_ui())
        self._setup_ui()
        self._create_connection()

    def create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.transactions_actions_widget = TransactionsActionsWidget(self)
        self.transactions_tab_widget = TransactionsTabWidget(self)
        count_layout = QHBoxLayout()
        self.count_label = QLabel()
        self.count_label.setObjectName("countLabel")
        count_layout.addWidget(self.count_label)
        count_layout.addStretch()
        main_layout.addWidget(self.transactions_actions_widget)
        main_layout.addWidget(self.transactions_tab_widget)
        main_layout.addLayout(count_layout)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_model()
        self.set_count_text(self.transactions_load_model_in.rowCount(), self.transactions_load_model_in.total_count)

    def _setup_texts(self) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.model_in_suffix = ui_texts.get("modelInSuffix", "")
        self.count_text = ui_texts.get("countLabelText", "Count:")

    def _setup_model(self) -> None:
        self._setup_in_model()
        self._setup_out_model()

    def _create_connection(self) -> None:
        self.transactions_actions_widget.in_transaction_button.clicked.connect(lambda: self.transactions_controller.create_transaction(TRANSFER_IN))
        self.transactions_actions_widget.out_transaction_button.clicked.connect(lambda: self.transactions_controller.create_transaction(TRANSFER_OUT))
        self.transactions_actions_widget.base_filter_combobox.currentIndexChanged.connect(self._on_index_changed)
        self.transactions_tab_widget.currentChanged.connect(self.transactions_controller.reset_model_data)

    def _setup_in_model(self) -> None:
        self.transactions_tab_widget.transaction_in_view.setModel(self.transactions_load_model_in)
        self.transactions_tab_widget.transaction_in_view.setup_texts()
        self.transactions_load_model_in.set_suffix(self.model_in_suffix)
        self.transactions_load_model_in.reload_transaction_data()
        self.transactions_tab_widget.transaction_in_view.customContextMenuRequested.connect(
            self.transactions_tab_widget.transaction_in_view.open_context_menu)

    def _setup_out_model(self) -> None:
        self.transactions_tab_widget.transactions_out_view.setModel(self.transactions_load_model_out)
        self.transactions_tab_widget.transactions_out_view.setup_texts()
        self.transactions_load_model_out.reload_transaction_data()
        self.transactions_tab_widget.transactions_out_view.customContextMenuRequested.connect(
            self.transactions_tab_widget.transactions_out_view.open_context_menu)

    def _on_index_changed(self) -> None:
        key = self.transactions_actions_widget.get_filter_key()
        if key:
            self.transactions_controller.set_basic_transactions_filter(key)

    def set_count_text(self, filtered: int, total: int) -> None:
        self.count_label.setText(f"{self.count_text} {filtered}/{total}")

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.setFocus()