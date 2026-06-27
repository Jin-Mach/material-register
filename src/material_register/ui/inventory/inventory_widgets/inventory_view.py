from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTableView

if TYPE_CHECKING:
    from material_register.ui.inventory.inventory_widget import InventoryWidget


class InventoryView(QTableView):
    def __init__(self, inventory_widget: "InventoryWidget") -> None:
        super().__init__(inventory_widget)