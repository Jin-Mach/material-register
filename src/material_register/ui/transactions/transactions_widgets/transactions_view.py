from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QHeaderView, QSizePolicy, QTableView

from material_register.config.ui_defaults import DEFAULT_TEXTS
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.headers_texts import HeadersTexts
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.transactions.transactions_widgets.transactions_context_menu import (
    TransactionsContextMenu,
)

if TYPE_CHECKING:
    from material_register.controllers.transactions_controller import (
        TransactionsController,
    )
    from material_register.ui.transactions.transactions_widgets.transactions_tab_widget import (
        TransactionsTabWidget,
    )


class TransactionsView(QTableView):
    def __init__(
        self,
        stacked_widget: "TransactionsTabWidget",
        transactions_controller: "TransactionsController",
    ) -> None:
        super().__init__(stacked_widget)
        self.setObjectName("transactionsView")
        self.transactions_controller = transactions_controller
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self._setup_behavior()

    def setup_texts(self) -> None:
        model = self.model()
        error = "TEXTS_LOAD_FAILED"
        if hasattr(model, "sourceModel"):
            model = model.sourceModel()
        if not HeadersTexts.set_transactions_headers_text(self, model):
            ErrorHandler.handle_error(
                f"Headers text load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = error
        self.menu_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not self.menu_texts:
            ErrorHandler.handle_error(
                f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = error
            self.menu_texts = DEFAULT_TEXTS.get(self.__class__.__name__, {})

    def _setup_behavior(self) -> None:
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def open_context_menu(self, position: QPoint) -> None:
        index = self.indexAt(position)
        if not index.isValid():
            return
        menu = TransactionsContextMenu(self, self.transactions_controller)
        menu.set_customer_index(index)
        if not self.menu_texts:
            ErrorHandler.handle_error(
                f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = True
        menu.set_ui_texts(self.menu_texts)
        menu.exec(self.mapToGlobal(position))
