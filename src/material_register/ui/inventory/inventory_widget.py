from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from material_register.controllers.inventory_controller import InventoryController
from material_register.db.models.inventory_proxy_filter import InventoryProxyFilter
from material_register.init.data_init import DataInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.inventory.inventory_widgets.inventory_actions_widget import (
    InventoryActionsWidget,
)
from material_register.ui.inventory.inventory_widgets.inventory_view import (
    InventoryView,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class InventoryWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.inventory_model = DataInit.inventory_model
        self.inventory_controller = InventoryController(self, self.inventory_model)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()
        self._apply_timer()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.inventory_actions_widget = InventoryActionsWidget(self)
        self.inventory_view = InventoryView(self)
        count_layout = QHBoxLayout()
        self.count_label = QLabel()
        self.count_label.setObjectName("countLabel")
        count_layout.addWidget(self.count_label)
        count_layout.addStretch()
        main_layout.addWidget(self.inventory_actions_widget)
        main_layout.addWidget(self.inventory_view)
        main_layout.addLayout(count_layout)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_model()
        self.inventory_view.setup_ui()

    def _setup_texts(self) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not ui_texts:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.count_text = ui_texts.get("countLabelText", "Count:")

    def _create_connection(self) -> None:
        self.inventory_actions_widget.search_line_edit.textChanged.connect(self._on_text_changed)

    def _setup_model(self) -> None:
        self.inventory_proxy_filter = InventoryProxyFilter()
        self.inventory_proxy_filter.setSourceModel(self.inventory_model)
        self.inventory_model.load_inventory_data()
        self.inventory_view.setModel(self.inventory_proxy_filter)
        self.active_proxy = self.inventory_proxy_filter
        self.inventory_controller.update_counts()

    def _on_text_changed(self) -> None:
        self.filter_timer.start()

    def _apply_filter(self) -> None:
        text = self.inventory_actions_widget.search_line_edit.text()
        self.inventory_controller.set_proxy_transactions_filter(text)

    def _apply_timer(self) -> None:
        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.setInterval(300)
        self.filter_timer.timeout.connect(self._apply_filter)

    def set_count_text(self, filtered: int, total: int) -> None:
        self.count_label.setText(f"{self.count_text} {filtered}/{total}")