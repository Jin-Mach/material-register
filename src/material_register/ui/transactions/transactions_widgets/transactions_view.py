from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableView, QHeaderView, QSizePolicy

from material_register.db.models.transactions_load_model_in import TransactionsLoadModelIn
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.headers_texts import HeadersTexts

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widgets.transactions_tab_widget import TransactionsTabWidget


class TransactionsView(QTableView):
    def __init__(self, stacked_widget: "TransactionsTabWidget") -> None:
        super().__init__(stacked_widget)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self._setup_behavior()

    def setup_texts(self) -> None:
        model = self.model()
        error = "TEXTS_LOAD_FAILED"
        if not isinstance(model, TransactionsLoadModelIn):
            return
        if not HeadersTexts.set_transactions_headers_text(self, model):
            ErrorHandler.handle_error(f"Headers text load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = error
        model.headerDataChanged.emit(Qt.Orientation.Horizontal, 0, model.columnCount() - 1)

    def _setup_behavior(self) -> None:
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)