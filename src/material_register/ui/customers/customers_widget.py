from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget

from material_register.controllers.customers.customers_controller import CustomersController
from material_register.init.models_init import ModelsSetup
from material_register.services.error_handler import ErrorHandler
from material_register.ui.customers.customers_widgets.customers_actions_widget import CustomersActionsWidget
from material_register.ui.customers.customers_widgets.customers_tab_widget import CustomersTabWidget
from material_register.ui.customers.customers_widgets.customers_view import CustomersView
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget
    from material_register.db.models.customers_model import CustomersModel


# noinspection PyUnresolvedReferences
class CustomersWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget"):
        super().__init__(stacked_widget)
        self.customers_controller = CustomersController(self)
        self.stacked_widget = stacked_widget
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.action_widget = CustomersActionsWidget(self)
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.tabBar().setElideMode(Qt.TextElideMode.ElideRight)
        main_layout.addWidget(self.action_widget)
        main_layout.addWidget(self.tab_widget)
        return main_layout

    def _setup_ui(self) -> None:
        self.customers_model = ModelsSetup.customers_model
        self.tabs_map = {}
        tabs_config = {
            "main_customers_view": {
                "view": CustomersTabWidget(CustomersView(self)),
                "name": "mainCustomersView",
            },
            "active_customers_view": {
                "view": CustomersTabWidget(CustomersView(self)),
                "name": "activeCustomersView",
            },
            "inactive_customers_view": {
                "view": CustomersTabWidget(CustomersView(self)),
                "name": "inactiveCustomersView",
            }
        }
        self._setup_tabs(tabs_config, self.customers_model)
        self.tab_widget.setCurrentIndex(0)
        QTimer.singleShot(0, self._init_counts)

    def _create_connection(self) -> None:
        self.action_widget.add_customer_button.clicked.connect(self.customers_controller.add_customer)
        self.tab_widget.currentChanged.connect(self.customers_controller.set_current_tab_filter)

    def _init_counts(self) -> None:
        self.customers_controller.set_current_tab_filter(0)
        self.customers_controller.update_counts()

    def _setup_tabs(self, tabs_config: dict, model: "CustomersModel") -> None:
        for key, view_data in tabs_config.items():
            tab_widget = view_data["view"]
            view_name = view_data["name"]
            tab_widget.customers_view.setModel(model)
            tab_widget.customers_view.setup_ui()
            tab_widget.customers_view.customContextMenuRequested.connect(
                tab_widget.customers_view.open_context_menu
            )
            tab_title = self._setup_texts(view_name)
            self.tab_widget.addTab(tab_widget, tab_title)
            self.tabs_map[key] = tab_widget

    def _setup_texts(self, view_name: str) -> str:
        default_text = "N/A"
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, default_text)
        if not ui_texts:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return default_text
        view_name += "Text"
        tab_text = ui_texts.get(view_name, default_text)
        return tab_text

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.setFocus()