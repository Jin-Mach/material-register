from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHeaderView, QTableView

from material_register.db.config.model_constants import MATERIAL_VIEW_HIDDEN_COLUMNS
from material_register.db.models.search_models.search_material_model import (
    SearchMaterialModel,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_WARNING, LOGGER_UI
from material_register.ui.setup.headers_texts import HeadersTexts

if TYPE_CHECKING:
    from material_register.ui.search.search_widgets.search_tab_widget import SearchTabWidget


class SearchMaterialView(QTableView):
    def __init__(self, search_tab_widget: "SearchTabWidget") -> None:
        super().__init__(search_tab_widget)
        self.setObjectName("searchMaterialView")

    def setup_ui(self) -> None:
        model = self.model()
        if not isinstance(model, SearchMaterialModel):
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

    def _setup_texts(self, model: SearchMaterialModel) -> None:
        if not HeadersTexts.set_headers_text(self, model):
            ErrorHandler.handle_error(
                f"Headers text load failed: {self.__class__.__name__}",
                LOGGER_UI,
                LOG_LEVEL_WARNING,
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"

    def _setup_columns(self, model: SearchMaterialModel) -> None:
        column_map = model.get_columns_map()
        for name in MATERIAL_VIEW_HIDDEN_COLUMNS:
            index = column_map.get(name)
            if index is not None:
                self.setColumnHidden(index, True)

    def _setup_behavior(self) -> None:
        self.setSizePolicy(
            self.sizePolicy().horizontalPolicy(),
            self.sizePolicy().verticalPolicy(),
        )
        self.verticalHeader().hide()
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(False)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)