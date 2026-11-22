from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHeaderView, QTableView

from material_register.db.models.inventory_models.inventory_history_model import (
    InventoryHistoryModel,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_WARNING, LOGGER_UI
from material_register.ui.setup.headers_texts import HeadersTexts

if TYPE_CHECKING:
    from material_register.ui.inventory.inventory_widgets.inventory_history_widget import (
        InventoryHistoryWidget,
    )


class InventoryHistoryView(QTableView):
    def __init__(self, inventory_history_widget: "InventoryHistoryWidget"):
        super().__init__(inventory_history_widget)

    def setup_ui(self) -> None:
        model = self.model()
        if not isinstance(model, InventoryHistoryModel):
            ErrorHandler.handle_error(
                f"Invalid model instance: {self.__class__.__name__}",
                LOGGER_UI,
                LOG_LEVEL_WARNING,
            )
            ErrorHandler.ui_texts_error = "UNKNOWN_ERROR"
            return
        self._setup_texts(model)
        self._setup_behavior()

    def _setup_texts(self, model: InventoryHistoryModel) -> None:
        if not HeadersTexts.set_inventory_history_headers_text(self, model):
            ErrorHandler.handle_error(
                f"Headers text load failed: {self.__class__.__name__}",
                LOGGER_UI,
                LOG_LEVEL_WARNING,
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"

    def _setup_behavior(self) -> None:
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(False)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)
