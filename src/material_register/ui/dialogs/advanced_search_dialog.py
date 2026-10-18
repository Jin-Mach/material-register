from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTabWidget, QVBoxLayout

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_WARNING, LOGGER_UI
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.search.search_widget import SearchWidget


class AdvancedSearchDialog(QDialog):
    def __init__(self, search_widget: "SearchWidget") -> None:
        super().__init__(search_widget)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.search_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.search_button.setObjectName("searchButton")
        self.cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        self.cancel_button.setObjectName("cancelButton")
        main_layout.addWidget(self.tab_widget)
        main_layout.addWidget(button_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_tabs()

    def _setup_texts(self) -> None:
        widgets = [self.search_button, self.cancel_button]
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__)
        self.transactions_tab_title = ui_texts.get("transactionsTabTitle", "")
        self.customers_tab_title = ui_texts.get("customersTabTitle", "")
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.search_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def _setup_tabs(self) -> None:
        pass
