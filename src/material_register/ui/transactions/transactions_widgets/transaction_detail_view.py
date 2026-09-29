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
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
)
from material_register.ui.setup.headers_texts import HeadersTexts

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widgets.transaction_detail_widget import (
        TransactionDetailWidget,
    )


class TransactionDetailView(QTableView):
    def __init__(self, transaction_detail_widget: "TransactionDetailWidget"):
        super().__init__(transaction_detail_widget)

    def setup_ui(self) -> None:
        model = self.model()
        if not isinstance(model, (TransactionItemsModelIn, TransactionItemsModelOut)):
            ErrorHandler.handle_error(
                f"Invalid model instance: {self.__class__.__name__}",
                LOGGER_UI,
                LOG_LEVEL_WARNING,
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
                f"Headers text load failed: {self.__class__.__name__}",
                LOGGER_UI,
                LOG_LEVEL_WARNING,
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
        self.verticalHeader().hide()
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.setSortingEnabled(True)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)
