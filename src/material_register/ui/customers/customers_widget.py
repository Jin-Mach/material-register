from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from material_register.controllers.customers_controller import CustomersController
from material_register.init.data_init import DataInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
)
from material_register.ui.customers.customers_widgets.customers_actions_widget import (
    CustomersActionsWidget,
)
from material_register.ui.customers.customers_widgets.customers_view import (
    CustomersView,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


# noinspection PyUnresolvedReferences
class CustomersWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.stacked_widget = stacked_widget
        self.customers_controller = CustomersController(self)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._init_counts()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        self.action_widget = CustomersActionsWidget(self)
        self.customers_view = CustomersView(self)
        self.customers_model = DataInit.customers_model
        self.actions_group_box = QGroupBox()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(5, 5, 5, 5)
        actions_layout.addWidget(self.action_widget)
        self.actions_group_box.setLayout(actions_layout)
        self.count_group_box = QGroupBox()
        count_layout = QHBoxLayout()
        count_layout.setSpacing(0)
        self.count_label = QLabel()
        self.count_label.setObjectName("countLabel")
        count_layout.addWidget(self.count_label)
        count_layout.addStretch()
        self.count_group_box.setLayout(count_layout)
        main_layout.addWidget(self.actions_group_box, 0)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.customers_view, 1)
        main_layout.addWidget(self.count_group_box, 0)
        return main_layout

    def _create_connection(self) -> None:
        self.action_widget.add_customer_button.clicked.connect(
            self.customers_controller.add_customer
        )

    def _init_counts(self) -> None:
        self.customers_controller.update_counts()

    def _setup_ui(self) -> None:
        self._setup_texts()
        self.customers_view.setModel(self.customers_model)
        QTimer.singleShot(0, self.customers_view.setup_ui)
        self.customers_view.customContextMenuRequested.connect(
            self.customers_view.open_context_menu
        )

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
        self.count_text = ui_texts.get("countLabelText", "Count: ")

    def set_count_text(self, filtered: int, total: int) -> None:
        self.count_label.setText(f"{self.count_text} {filtered}/{total}")

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.setFocus()
