from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.styles_constants import PRICE_STYLE
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    UI_MARGINS_5,
    UI_SPACING,
)
from material_register.ui.search.search_widgets.search_detail_widget import SearchDetailWidget
from material_register.ui.setup.ui_texts import UiTexts
from material_register.utils.formatting_utils import format_number_to_locale

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class SearchWidget(QWidget):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        self.search_detail_widget = SearchDetailWidget(self)
        self.actions_group_box = QGroupBox()
        self.actions_group_box.setObjectName("actionsGroupBox")
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(*UI_MARGINS_5)
        action_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.actions_group_box.setLayout(action_layout)
        self.detail_group_box = QGroupBox()
        self.detail_group_box.setObjectName("detailGroupBox")
        detail_group_layout = QVBoxLayout()
        detail_group_layout.setContentsMargins(*UI_MARGINS_5)
        detail_group_layout.addWidget(self.search_detail_widget)
        self.detail_group_box.setLayout(detail_group_layout)
        self.transactions_group_box = QGroupBox()
        self.transactions_group_box.setObjectName("transactionsGroupBox")
        transactions_group_layout = QVBoxLayout()
        transactions_group_layout.setContentsMargins(*UI_MARGINS_5)
        transactions_group_layout.addSpacing(5)
        self.transactions_group_box.setLayout(transactions_group_layout)
        count_group_box = QGroupBox()
        count_layout = QHBoxLayout()
        count_layout.setSpacing(0)
        self.items_count_label = QLabel()
        self.items_count_label.setObjectName("itemsCountLabel")
        self.price_count_label = QLabel()
        self.price_count_label.setObjectName("priceCountLabel")
        self.price_count_value = QLabel()
        self.price_count_value.setObjectName("priceCountValue")
        count_layout.addWidget(self.items_count_label)
        count_layout.addStretch()
        count_layout.addWidget(self.price_count_label)
        count_layout.addWidget(self.price_count_value)
        count_group_box.setLayout(count_layout)
        main_layout.addWidget(self.actions_group_box, 0)
        main_layout.addWidget(self.detail_group_box, 0)
        main_layout.addWidget(self.transactions_group_box, 1)
        main_layout.addWidget(count_group_box)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()

    def _setup_texts(self) -> None:
        widgets = [self.detail_group_box, self.transactions_group_box]
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.items_count_text = ui_texts.get("itemsCountLabelText", "Count:")
        self.price_prefix = ui_texts.get("pricePrefix", "")
        self.price_sufix = ui_texts.get("priceSuffix", "")
        self.tooltip_texts = {
            "customer_text": ui_texts.get("tooltipCustomerText", "Customer:"),
            "address_text": ui_texts.get("tooltipAddressText", "Address:"),
            "payment_text": ui_texts.get("tooltipPaymentText", "Payment:"),
            "CASH": ui_texts.get("CASH", "Cash"),
            "TRANSFER": ui_texts.get("TRANSFER", "Transfer"),
            "notes_text": ui_texts.get("tooltipNotesText", "Notes:"),
        }
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _setup_style(self) -> None:
        font = QFont()
        font.setBold(True)
        self.price_count_value.setStyleSheet(PRICE_STYLE)
        self.price_count_value.setFont(font)

    def set_count_text(self, filtered: int, total: int) -> None:
        self.items_count_label.setText(f"{self.items_count_text} {filtered}/{total}")

    def set_price_text(self, total_price: float) -> None:
        self.price_count_label.setText(f"{self.price_prefix}")
        self.price_count_value.setText(
            f"{format_number_to_locale(total_price)} {self.price_sufix}"
        )
