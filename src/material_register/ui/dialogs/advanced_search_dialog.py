from typing import TYPE_CHECKING

from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import QDialog, QDialogButtonBox, QTabWidget, QVBoxLayout

from material_register.domain.adavanced_search_dataclass import AdvancedSearchDataclass
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    UI_MARGINS_10,
    UI_SPACING,
)
from material_register.ui.dialogs.advanced_search_widgets.transactions_search_widget import (
    TransactionsSearchWidget,
)
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
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_10)
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
        if not ui_texts:
            ErrorHandler.handle_error(
                f"Texts load failed: {self.__class__.__name__}",
                LOGGER_UI,
                LOG_LEVEL_WARNING,
            )
            ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
            return
        self.transactions_tab_title = ui_texts.get("transacationsTabTitleText", "")
        self.customers_tab_title = ui_texts.get("customersTabTitleText", "")
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
        self.transactions_search_widget = TransactionsSearchWidget(self)
        self.tab_widget.addTab(
            self.transactions_search_widget, self.transactions_tab_title
        )

    def get_advanced_filters(self) -> list[AdvancedSearchDataclass]:
        advanced_filters = []
        filters = [self.transactions_search_widget.get_filters_data()]
        for section_filters in filters:
            if section_filters:
                advanced_filters.extend(section_filters)
        return advanced_filters

    def showEvent(self, event: QShowEvent) -> None:
        self.adjustSize()
        self.setFixedSize(self.width() + 10, self.height() + 10)
        super().showEvent(event)
