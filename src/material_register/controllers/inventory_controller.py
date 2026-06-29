from typing import TYPE_CHECKING

from material_register.ui.dialogs.message_boxes import MessageBoxes
from material_register.utils.normalizer import normalize_text

if TYPE_CHECKING:
    from material_register.ui.inventory.inventory_widget import InventoryWidget
    from material_register.db.models.inventory_model import InventoryModel


class InventoryController:
    def __init__(self, inventory_widget: "InventoryWidget", inventory_model: "InventoryModel") -> None:
        self.inventory_widget = inventory_widget
        self.inventory_model = inventory_model

    def set_proxy_transactions_filter(self, search_text: str) -> None:
        text = normalize_text(search_text)
        proxy_model = self.inventory_widget.active_proxy
        if proxy_model is None:
            return
        proxy_model.set_filtered_text(text)
        if proxy_model.rowCount() == 0:
            self.inventory_widget.inventory_actions_widget.search_line_edit.selectAll()
            MessageBoxes.show_error(self.inventory_widget, "NO_RESULTS", "WARNING")
            proxy_model.set_filtered_text("")
            return
        self.update_counts()

    def update_counts(self) -> None:
        self.inventory_widget.set_count_text(self.inventory_widget.active_proxy.rowCount(),
                                             self.inventory_model.rowCount())