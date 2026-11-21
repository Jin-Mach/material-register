from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHeaderView, QTableView

if TYPE_CHECKING:
    from material_register.ui.inventory.inventory_widgets.inventory_history_widget import (
        InventoryHistoryWidget,
    )


class InventoryHistoryView(QTableView):
    def __init__(self, inventory_history_widget: "InventoryHistoryWidget"):
        super().__init__(inventory_history_widget)
        self.setup_ui()

    def setup_ui(self) -> None:
        self._setup_behavior()

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
