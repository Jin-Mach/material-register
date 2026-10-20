from typing import TYPE_CHECKING

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLineEdit, QPushButton, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    UI_MARGINS_5,
    UI_SPACING,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.search.search_widget import SearchWidget


class SearchActionsWidget(QWidget):
    def __init__(self, search_widget: "SearchWidget") -> None:
        super().__init__(search_widget)
        self.search_widget = search_widget
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        main_layout.setSpacing(UI_SPACING * 2)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        self.invisible_in_button = QPushButton()
        self.invisible_in_button.setObjectName("invisibleInButton")
        self.invisible_in_button.setEnabled(False)
        self.invisible_out_button = QPushButton()
        self.invisible_out_button.setObjectName("invisibleOutButton")
        self.invisible_out_button.setEnabled(False)
        self.base_filter_combobox = QComboBox()
        self.base_filter_combobox.setObjectName("baseFilterCombobox")
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setObjectName("searchLineEdit")
        self.search_line_edit.setMinimumWidth(400)
        self.search_button = QPushButton()
        self.search_button.setObjectName("searchButton")
        self.reset_filter_button = QPushButton()
        self.reset_filter_button.setObjectName("resetFilterButton")
        self.create_filter_button = QPushButton()
        self.create_filter_button.setObjectName("createFilterButton")
        main_layout.addWidget(self.invisible_in_button)
        main_layout.addWidget(self.invisible_out_button)
        main_layout.addWidget(self.base_filter_combobox)
        main_layout.addWidget(self.search_line_edit, 1)
        main_layout.addStretch()
        main_layout.addWidget(self.search_button)
        main_layout.addWidget(self.reset_filter_button)
        main_layout.addWidget(self.create_filter_button)
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [
            self.search_line_edit,
            self.search_button,
            self.reset_filter_button,
            self.create_filter_button,
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
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _create_connection(self) -> None:
        self.search_line_edit.returnPressed.connect(self._start_basic_filter)
        self.search_button.clicked.connect(self._start_basic_filter)
        self.reset_filter_button.clicked.connect(self._reset_filter)
        self.create_filter_button.clicked.connect(
            self.search_widget.advanced_search_controller.start_advanced_filter
        )

    def _start_basic_filter(self) -> None:
        period_key = self._get_filter_key()
        value = self.search_line_edit.text().strip()
        self.search_widget.search_controller.start_basic_filter(period_key, value)

    def _reset_filter(self) -> None:
        self.search_widget.search_controller.start_basic_filter(None, [])
        self.base_filter_combobox.setCurrentIndex(0)
        self.search_line_edit.clear()

    def set_search_buttons_state(self, disabled: bool) -> None:
        self.search_button.setDisabled(disabled)
        self.reset_filter_button.setDisabled(disabled)
        self.create_filter_button.setDisabled(disabled)

    def _get_filter_key(self) -> str | None:
        filter_map = {
            0: None,
            1: "today",
            2: "week",
            3: "month",
            4: "year",
        }
        return filter_map[self.base_filter_combobox.currentIndex()]
