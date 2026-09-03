from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QSizePolicy, QTabWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.transactions.transactions_widgets.transactions_view import (
    TransactionsView,
)

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


class TransactionsTabWidget(QTabWidget):
    def __init__(self, transactions_widget: "TransactionsWidget") -> None:
        super().__init__(transactions_widget)
        self.transactions_widget = transactions_widget
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._setup_ui()
        self._create_connection()
        self.transaction_index = None

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_tabs()

    def _setup_texts(self) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            ErrorHandler.handle_error(
                f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.in_tab_title = ui_texts.get("inTabTitleText", "IN")
        self.out_tab_title = ui_texts.get("outTabTitleText", "OUT")

    def _setup_tabs(self) -> None:
        self.transaction_in_view = TransactionsView(
            self, self.transactions_widget.transactions_controller
        )
        self.transactions_out_view = TransactionsView(
            self, self.transactions_widget.transactions_controller
        )
        self.addTab(self.transaction_in_view, self.in_tab_title)
        self.addTab(self.transactions_out_view, self.out_tab_title)

    def _create_connection(self) -> None:
        self.transaction_in_view.doubleClicked.connect(self._update_transaction)
        self.transactions_out_view.doubleClicked.connect(self._update_transaction)

    def _update_transaction(self, index: QModelIndex) -> None:
        self.transaction_index = index
        self.transactions_widget.transactions_controller.update_transaction(
            self.transaction_index
        )
