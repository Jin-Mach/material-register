from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStackedWidget

from material_register.ui.catalog.catalog_widget import CatalogWidget
from material_register.ui.customers.customers_widget import CustomersWidget
from material_register.ui.export.period_export_widget import PeriodExportWidget
from material_register.ui.inventory.inventory_widget import InventoryWidget
from material_register.ui.settings.settings_widget import SettingsWidget
from material_register.ui.transactions.transactions_widget import TransactionsWidget

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class StackedWidget(QStackedWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.transactions_widget = TransactionsWidget(self)
        self.inventory_widget = InventoryWidget(self)
        self.period_export_widget = PeriodExportWidget(self)
        self.customers_widget = CustomersWidget(self)
        self.catalog_widget = CatalogWidget(self)
        self.settings_widget = SettingsWidget(self)
        self.init_setup()

    def init_setup(self) -> None:
        widgets = [
            self.transactions_widget,
            self.inventory_widget,
            self.period_export_widget,
            self.customers_widget,
            self.catalog_widget,
            self.settings_widget,
        ]
        for widget in widgets:
            self.addWidget(widget)
