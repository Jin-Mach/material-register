from typing import TYPE_CHECKING

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit, QPushButton, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.transactions.transactions_widget import TransactionsWidget


class TransactionsActionsWidget(QWidget):
    def __init__(self, transactions_widget: "TransactionsWidget") -> None:
        super().__init__(transactions_widget)
        self.setLayout(self.create_ui())
        self._ui_setup()

    def create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        self.in_transaction_button = QPushButton()
        self.in_transaction_button.setObjectName("inTransactionButton")
        self.out_transaction_button = QPushButton()
        self.out_transaction_button.setObjectName("outTransactionButton")
        self.base_filter_combobox = QComboBox()
        self.base_filter_combobox.setObjectName("baseFilterCombobox")
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setObjectName("searchLineEdit")
        self.search_line_edit.setMinimumWidth(600)
        main_layout.addWidget(self.in_transaction_button)
        main_layout.addWidget(self.out_transaction_button)
        main_layout.addWidget(self.base_filter_combobox)
        main_layout.addWidget(self.search_line_edit)
        main_layout.addStretch()
        return main_layout

    def _ui_setup(self) -> None:
        widgets = [
            self.in_transaction_button,
            self.out_transaction_button,
            self.search_line_edit,
        ]
        self._setup_texts(widgets)
        self.base_filter_combobox.setCurrentIndex(0)

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        filter_items = ui_texts.get(
            f"{self.base_filter_combobox.objectName()}Items", []
        )
        self.base_filter_combobox.addItems(filter_items)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def get_filter_key(self) -> str:
        filter_map = {
            0: "today",
            1: "week",
            2: "month",
            3: "year",
        }
        return filter_map[self.base_filter_combobox.currentIndex()]
