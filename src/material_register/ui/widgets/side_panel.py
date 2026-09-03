from typing import TYPE_CHECKING

from PySide6.QtWidgets import QButtonGroup, QGroupBox, QPushButton, QVBoxLayout, QWidget

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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        group_box = QGroupBox()
        group_box.setObjectName("sidePanelGroupBox")
        group_box_layout = QVBoxLayout()
        group_box_layout.setSpacing(5)
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
        group_box_layout.addWidget(self.transactions_button)
        group_box_layout.addWidget(self.inventory_button)
        group_box_layout.addWidget(self.export_button)
        group_box_layout.addWidget(self.customers_button)
        group_box_layout.addWidget(self.catalog_button)
        group_box_layout.addStretch()
        group_box_layout.addWidget(self.settings_button)
        group_box.setLayout(group_box_layout)
        main_layout.addWidget(group_box)
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
        ]
        for widget in widgets:
            widget.setCheckable(True)
