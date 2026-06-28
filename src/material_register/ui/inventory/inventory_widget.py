from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout

from material_register.init.data_init import DataInit
from material_register.ui.inventory.inventory_widgets.inventory_view import InventoryView
from material_register.ui.inventory.inventory_widgets.inventory_actions_widget import InventoryActionsWidget

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class InventoryWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.model = DataInit.inventory_model
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.inventory_actions_widget = InventoryActionsWidget(self)
        self.inventory_view = InventoryView(self)
        main_layout.addWidget(self.inventory_actions_widget)
        main_layout.addWidget(self.inventory_view)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_model()
        self.inventory_view.setup_ui()

    def _setup_model(self) -> None:
        self.model.load_inventory_data()
        self.inventory_view.setModel(self.model)