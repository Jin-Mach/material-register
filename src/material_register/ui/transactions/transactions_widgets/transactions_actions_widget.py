from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class TransactionsActionsWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)
        self.setLayout(self.create_ui())
        self._ui_setup()

    def create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        self.in_transaction_button = QPushButton()
        self.in_transaction_button.setObjectName("inTransactionButton")
        self.out_transaction_button = QPushButton()
        self.out_transaction_button.setObjectName("outTransactionButton")
        main_layout.addWidget(self.in_transaction_button)
        main_layout.addWidget(self.out_transaction_button)
        main_layout.addStretch()
        return main_layout

    def _ui_setup(self) -> None:
        widgets = [self.in_transaction_button, self.out_transaction_button]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return