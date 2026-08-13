from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHeaderView, QTableView

from material_register.db.config.model_constants import (
    INVENTORY_COLUMNS_MAP,
    INVENTORY_VIEW_HIDDEN_COLUMNS,
)
from material_register.db.models.inventory_proxy_filter import InventoryProxyFilter
from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.headers_texts import HeadersTexts

if TYPE_CHECKING:
    from material_register.ui.inventory.inventory_widget import InventoryWidget


class InventoryView(QTableView):
    def __init__(self, inventory_widget: "InventoryWidget") -> None:
        super().__init__(inventory_widget)
        self.setObjectName("inventoryView")

    def setup_ui(self) -> None:
        model = self.model()
        error = "TEXTS_LOAD_FAILED"
        if not isinstance(model, InventoryProxyFilter):
            return
        if not HeadersTexts.set_inventory_headers_text(self, model):
            ErrorHandler.handle_error(
                f"Headers text load failed: {self.__class__.__name__}", "ui", "warning"
            )
            ErrorHandler.ui_texts_error = error
        self._setup_columns()
        self._setup_headers(model)
        self._setup_behavior()

    def _setup_columns(self) -> None:
        for column_name in INVENTORY_VIEW_HIDDEN_COLUMNS:
            column_index = INVENTORY_COLUMNS_MAP.get(column_name)
            if column_index is not None:
                self.setColumnHidden(column_index, True)

    def _setup_headers(self, model: InventoryProxyFilter) -> None:
        header = self.horizontalHeader()
        active_column = INVENTORY_COLUMNS_MAP["commodity_active"]
        for col in range(model.columnCount()):
            if col == active_column:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
            else:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
        self.resizeColumnsToContents()

    def _setup_behavior(self) -> None:
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)
