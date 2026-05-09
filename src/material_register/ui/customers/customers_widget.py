from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QWidget, QVBoxLayout

from material_register.controllers.customers.customers_controller import CustomersController
from material_register.init.models_init import ModelsSetup
from material_register.ui.customers.customers_widgets.customers_actions_widget import CustomersActionsWidget
from material_register.ui.customers.customers_widgets.customers_view import CustomersView

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


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
        self.customers_model = ModelsSetup.customers_model
        self.customers_view = CustomersView(self)
        main_layout.addWidget(self.action_widget)
        main_layout.addWidget(self.customers_view)
        return main_layout

    def _setup_ui(self) -> None:
        self.customers_view.setModel(self.customers_model)
        self.customers_view.setup_ui()

    def _create_connection(self) -> None:
        self.action_widget.add_customer_button.clicked.connect(self.customers_controller.add_customers)

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.setFocus()