from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QPushButton, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.customers.customers_widget import CustomersWidget


class CustomersActionsWidget(QWidget):
    def __init__(self, customer_widget: "CustomersWidget") -> None:
        super().__init__(customer_widget)
        self.customer_widget = customer_widget
        self.setLayout(self._create_ui())
        self._setup_texts()
        self._create_connection()
        self._apply_timer()

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        self.add_customer_button = QPushButton()
        self.add_customer_button.setObjectName("addCustomerButton")
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setObjectName("searchLineEdit")
        self.search_line_edit.setMinimumWidth(600)
        main_layout.addWidget(self.add_customer_button)
        main_layout.addStretch()
        main_layout.addWidget(self.search_line_edit)
        main_layout.addStretch()
        return main_layout

    def _setup_texts(self) -> None:
        widgets = [self.add_customer_button, self.search_line_edit]
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _create_connection(self) -> None:
        self.search_line_edit.textChanged.connect(self._on_text_changed)

    def _on_text_changed(self) -> None:
        self.filter_timer.start()

    def _apply_filter(self) -> None:
        self.customer_widget.customers_controller.filter_customers(
            self.search_line_edit.text().strip()
        )

    def _apply_timer(self) -> None:
        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.setInterval(300)
        self.filter_timer.timeout.connect(self._apply_filter)
