from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

from material_register.ui.dialogs.error_dialog import ErrorDialog
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
            dialog = ErrorDialog()
            dialog.show_dialog("TEXTS_LOAD_FAILED", False)