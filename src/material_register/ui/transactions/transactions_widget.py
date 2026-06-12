from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout

from material_register.config.app_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.controllers.transactions_controller import TransactionsController
from material_register.db.models.transactions_load_model_in import TransactionsLoadModelIn
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
        self.transactions_load_model_in = TransactionsLoadModelIn(self.db_connection)
        self.transactions_controller = TransactionsController(self)
        self.setLayout(self.create_ui())
        self._setup_ui()
        self._create_connection()

    def create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.actions_widget = TransactionsActionsWidget(self.stacked_widget)
        self.transactions_tab_widget = TransactionsTabWidget(self.stacked_widget)
        main_layout.addWidget(self.actions_widget)
        main_layout.addWidget(self.transactions_tab_widget)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_model()

    def _setup_texts(self) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.model_in_suffix = ui_texts.get("modelInSuffix", "")

    def _setup_model(self) -> None:
        self._setup_in_model()

    def _create_connection(self) -> None:
        self.actions_widget.in_transaction_button.clicked.connect(lambda: self.transactions_controller.create_transaction(TRANSFER_IN))
        self.actions_widget.out_transaction_button.clicked.connect(lambda: self.transactions_controller.create_transaction(TRANSFER_OUT))

    def _setup_in_model(self) -> None:
        self.transactions_tab_widget.transaction_in_view.setModel(self.transactions_load_model_in)
        self.transactions_tab_widget.transaction_in_view.setup_texts()
        self.transactions_load_model_in.set_suffix(self.model_in_suffix)
        self.transactions_load_model_in.reload_transaction_data()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.setFocus()