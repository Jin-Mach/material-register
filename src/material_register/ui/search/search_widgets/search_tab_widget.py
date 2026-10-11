from typing import TYPE_CHECKING

from PySide6.QtWidgets import QSizePolicy, QTabWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
)
from material_register.ui.search.search_widgets.search_material_view import (
    SearchMaterialView,
)
from material_register.ui.search.search_widgets.search_transactions_view import (
    SearchTransactionsView,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.search.search_widget import SearchWidget


class SearchTabWidget(QTabWidget):
    def __init__(self, search_widget: "SearchWidget") -> None:
        super().__init__(search_widget)
        self.search_widget = search_widget
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_tabs()

    def _setup_texts(self) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            ErrorHandler.handle_error(
                f"Texts load failed: {self.__class__.__name__}",
                LOGGER_UI,
                LOG_LEVEL_WARNING,
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.transactions_tab_title = ui_texts.get(
            "transactionsTabTitleText", "Transactions"
        )
        self.material_tab_title = ui_texts.get("materialTabTitleText", "Material")

    def _setup_tabs(self) -> None:
        self.transactions_tab = SearchTransactionsView(
            self, self.search_widget.search_document_controller
        )
        self.material_tab = SearchMaterialView(self)
        self.addTab(self.transactions_tab, self.transactions_tab_title)
        self.addTab(self.material_tab, self.material_tab_title)
