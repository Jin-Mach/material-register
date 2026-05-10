from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class SidePanel(QWidget):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.setLayout(self._create_ui())
        self._ui_setup()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.transactions_button = QPushButton()
        self.transactions_button.setObjectName("transactionsButton")
        self.customers_button = QPushButton()
        self.customers_button.setObjectName("customersButton")
        main_layout.addWidget(self.transactions_button)
        main_layout.addWidget(self.customers_button)
        main_layout.addStretch()
        return main_layout

    def _ui_setup(self) -> None:
        if not UiTexts.set_ui_texts(self, [self.transactions_button, self.customers_button]):
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return