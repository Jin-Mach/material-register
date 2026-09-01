from typing import TYPE_CHECKING

from PySide6.QtWidgets import QButtonGroup, QPushButton, QVBoxLayout, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class SidePanel(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.transactions_button = QPushButton()
        self.transactions_button.setObjectName("transactionsButton")
        self.inventory_button = QPushButton()
        self.inventory_button.setObjectName("inventoryButton")
        self.export_button = QPushButton()
        self.export_button.setObjectName("exportButton")
        self.customers_button = QPushButton()
        self.customers_button.setObjectName("customersButton")
        self.catalog_button = QPushButton()
        self.catalog_button.setObjectName("catalogButton")
        self.settings_button = QPushButton()
        self.settings_button.setObjectName("settingsButton")
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.addButton(self.transactions_button)
        self.button_group.addButton(self.inventory_button)
        self.button_group.addButton(self.export_button)
        self.button_group.addButton(self.customers_button)
        self.button_group.addButton(self.catalog_button)
        self.button_group.addButton(self.settings_button)
        main_layout.addWidget(self.transactions_button)
        main_layout.addWidget(self.inventory_button)
        main_layout.addWidget(self.export_button)
        main_layout.addWidget(self.customers_button)
        main_layout.addWidget(self.catalog_button)
        main_layout.addStretch()
        main_layout.addWidget(self.settings_button)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_buttons()

    def _setup_texts(self) -> None:
        widgets = [
            self.transactions_button,
            self.inventory_button,
            self.export_button,
            self.customers_button,
            self.catalog_button,
            self.settings_button,
        ]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_buttons(self) -> None:
        widgets = [
            self.transactions_button,
            self.inventory_button,
            self.export_button,
            self.customers_button,
            self.catalog_button,
            self.settings_button,
        ]
        for widget in widgets:
            widget.setCheckable(True)
