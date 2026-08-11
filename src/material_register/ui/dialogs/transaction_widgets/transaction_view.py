from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHeaderView, QTableView

from material_register.db.config.model_constants import TRANSACTION_VIEW_HIDDEN_COLUMNS
from material_register.db.models.transaction_items_model_in import (
    TransactionItemsModelIn,
)
from material_register.db.models.transaction_items_model_out import (
    TransactionItemsModelOut,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.headers_texts import HeadersTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.transaction_widgets.transactions_items_widget import (
        TransactionsItemsWidget,
    )


class TransactionView(QTableView):
    def __init__(self, transaction_items_widget: "TransactionsItemsWidget"):
        super().__init__(transaction_items_widget)

    def setup_ui(self) -> None:
        model = self.model()
        if not isinstance(model, (TransactionItemsModelIn, TransactionItemsModelOut)):
            ErrorHandler.handle_error(
                f"Invalid model instance: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = "UNKNOWN_ERROR"
            return
        self._setup_texts(model)
        self._setup_columns(model)
        self._setup_behavior()

    def _setup_texts(
        self, model: TransactionItemsModelIn | TransactionItemsModelOut
    ) -> None:
        if not HeadersTexts.set_headers_text(self, model):
            ErrorHandler.handle_error(
                f"Headers text load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"

    def _setup_columns(
        self, model: TransactionItemsModelIn | TransactionItemsModelOut
    ) -> None:
        column_map = model.get_columns_map()
        for name in TRANSACTION_VIEW_HIDDEN_COLUMNS:
            index = column_map.get(name)
            if index is not None:
                self.setColumnHidden(index, True)

    def _setup_behavior(self) -> None:
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)
