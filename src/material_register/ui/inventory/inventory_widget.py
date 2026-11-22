from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QTimer
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from material_register.controllers.inventory_controller import InventoryController
from material_register.controllers.inventory_history_controller import (
    InventoryHistoryController,
)
from material_register.db.models.inventory_models.inventory_proxy_model import (
    InventoryProxyModel,
)
from material_register.init.data_init import DataInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    UI_MARGINS_5,
    UI_SPACING,
)
from material_register.ui.inventory.inventory_widgets.inventory_actions_widget import (
    InventoryActionsWidget,
)
from material_register.ui.inventory.inventory_widgets.inventory_history_widget import (
    InventoryHistoryWidget,
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
        self.inventory_history_controller = InventoryHistoryController(self)

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        self.inventory_actions_widget = InventoryActionsWidget(self)
        self.actions_group_box = QGroupBox()
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(UI_SPACING)
        actions_layout.setContentsMargins(*UI_MARGINS_5)
        actions_layout.addWidget(self.inventory_actions_widget)
        self.actions_group_box.setLayout(actions_layout)
        inventory_layout = QHBoxLayout()
        inventory_layout.setSpacing(UI_SPACING)
        inventory_layout.setContentsMargins(0, 0, 0, 0)
        self.inventory_history_widget = InventoryHistoryWidget(self)
        self.inventory_history_group_box = QGroupBox()
        history_layout = QHBoxLayout()
        history_layout.setSpacing(UI_SPACING)
        history_layout.setContentsMargins(*UI_MARGINS_5)
        history_layout.addWidget(self.inventory_history_widget)
        self.inventory_history_group_box.setLayout(history_layout)
        self.inventory_view = InventoryView(self)
        self.inventory_group_box = QGroupBox()
        inventory_view_layout = QHBoxLayout()
        inventory_view_layout.setSpacing(UI_SPACING)
        inventory_view_layout.setContentsMargins(*UI_MARGINS_5)
        inventory_view_layout.addWidget(self.inventory_view)
        self.inventory_group_box.setLayout(inventory_view_layout)
        inventory_layout.addWidget(self.inventory_history_group_box)
        inventory_layout.addWidget(self.inventory_group_box, 1)
        self.count_group_box = QGroupBox()
        count_layout = QHBoxLayout()
        count_layout.setSpacing(0)
        self.count_label = QLabel()
        self.count_label.setObjectName("countLabel")
        count_layout.addWidget(self.count_label)
        count_layout.addStretch()
        self.count_group_box.setLayout(count_layout)
        main_layout.addWidget(self.actions_group_box, 0)
        main_layout.addLayout(inventory_layout, 1)
        main_layout.addWidget(self.count_group_box, 0)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_model()
        self.inventory_view.setup_ui()

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
        self.count_text = ui_texts.get("countLabelText", "Count:")

    def _create_connection(self) -> None:
        self.inventory_actions_widget.search_line_edit.textChanged.connect(
            self._on_text_changed
        )
        self.inventory_view.selectionModel().currentChanged.connect(
            self._reload_history
        )

    def _setup_model(self) -> None:
        self.inventory_proxy_model = InventoryProxyModel()
        self.inventory_proxy_model.setSourceModel(self.inventory_model)
        self.inventory_model.load_inventory_data()
        self.inventory_view.setModel(self.inventory_proxy_model)
        self.active_proxy = self.inventory_proxy_model
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

    def _reload_history(self, selected: QModelIndex, _: QModelIndex) -> None:
        if not selected.isValid():
            return
        model_index = self.active_proxy.mapToSource(selected)
        commodity_id, commodity_name, commodity_unit = (
            self.inventory_model.get_commodity_data(model_index)
        )
        if commodity_id is None:
            return
        if commodity_name is not None:
            self.inventory_history_widget.set_info_text(commodity_name)
        from_date, to_date = self.inventory_history_widget.get_date_range()
        self.inventory_history_controller.reload_commodity_history(
            commodity_id, from_date, to_date, commodity_unit
        )

    def set_count_text(self, filtered: int, total: int) -> None:
        self.count_label.setText(f"{self.count_text} {filtered}/{total}")
