from typing import TYPE_CHECKING

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QButtonGroup,
    QDateEdit,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from material_register.init.data_init import DataInit
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    UI_MARGINS_5,
    UI_MARGINS_10,
    UI_SPACING,
)
from material_register.ui.inventory.inventory_widgets.inventory_history_view import (
    InventoryHistoryView,
)
from material_register.ui.setup.ui_texts import UiTexts
from material_register.utils.date_filters import get_filter_range
from material_register.utils.formatting_utils import format_date_to_utc

if TYPE_CHECKING:
    from material_register.ui.inventory.inventory_widget import InventoryWidget


class InventoryHistoryWidget(QWidget):
    def __init__(self, inventory_widget: "InventoryWidget"):
        super().__init__(inventory_widget)
        self.inventory_history_model = DataInit.inventory_history_model
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        info_group = self._create_info_group()
        date_options_group = self._create_date_options_group()
        self.inventory_history_view = InventoryHistoryView(self)
        total_group = self._create_total_group()
        main_layout.addWidget(info_group)
        main_layout.addWidget(date_options_group)
        main_layout.addWidget(self.inventory_history_view, 1)
        main_layout.addWidget(total_group)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_model()
        self._setup_date_edits()
        self._apply_date_state()
        self.today_radio_button.setChecked(True)
        self.set_info_text("")
        self.set_count_text(0)
        self.set_value_text(0, "")

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.count_text = ui_texts.get("countLabelText", "Count:")
        self.value_text = ui_texts.get("valueLabelText", "Total:")
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
        date_radiobuttons = [
            self.today_radio_button,
            self.week_radio_button,
            self.month_radio_button,
            self.year_radio_button,
            self.custom_radio_button,
        ]
        for radio_button in date_radiobuttons:
            radio_button.toggled.connect(self._apply_date_state)
        self.from_date_edit.dateChanged.connect(self._update_to_date_minimum)
        self.to_date_edit.dateChanged.connect(self._update_from_date_maximum)

    def _setup_model(self) -> None:
        self.inventory_history_view.setModel(self.inventory_history_model)

    def _create_info_group(self) -> QGroupBox:
        info_group = QGroupBox()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        self.info_label = QLabel()
        main_layout.addStretch()
        main_layout.addWidget(self.info_label)
        main_layout.addStretch()
        info_group.setLayout(main_layout)
        return info_group

    def _create_date_options_group(self) -> QGroupBox:
        date_options_group_box = QGroupBox()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING * 2)
        main_layout.setContentsMargins(*UI_MARGINS_10)
        self.time_button_group = QButtonGroup()
        standard_time_layout = QHBoxLayout()
        self.today_radio_button = QRadioButton()
        self.today_radio_button.setObjectName("todayRadioButton")
        self.week_radio_button = QRadioButton()
        self.week_radio_button.setObjectName("weekRadioButton")
        self.month_radio_button = QRadioButton()
        self.month_radio_button.setObjectName("monthRadioButton")
        self.year_radio_button = QRadioButton()
        self.year_radio_button.setObjectName("yearRadioButton")
        custom_time_layout = QHBoxLayout()
        custom_time_layout.setSpacing(UI_SPACING * 2)
        self.custom_radio_button = QRadioButton()
        self.custom_radio_button.setObjectName("customRadioButton")
        from_to_layout = QHBoxLayout()
        from_to_layout.setSpacing(UI_SPACING)
        self.from_date_label = QLabel()
        self.from_date_label.setObjectName("fromDateLabel")
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        separator_label = QLabel("-")
        self.from_date_edit.setObjectName("fromDateEdit")
        self.to_date_label = QLabel()
        self.to_date_label.setObjectName("toDateLabel")
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setObjectName("toDateEdit")
        self.time_button_group.addButton(self.today_radio_button)
        self.time_button_group.addButton(self.week_radio_button)
        self.time_button_group.addButton(self.month_radio_button)
        self.time_button_group.addButton(self.year_radio_button)
        self.time_button_group.addButton(self.custom_radio_button)
        standard_time_layout.addWidget(self.today_radio_button)
        standard_time_layout.addWidget(self.week_radio_button)
        standard_time_layout.addWidget(self.month_radio_button)
        standard_time_layout.addWidget(self.year_radio_button)
        standard_time_layout.addStretch()
        from_to_layout.addWidget(self.from_date_label)
        from_to_layout.addWidget(self.from_date_edit)
        from_to_layout.addWidget(separator_label)
        from_to_layout.addWidget(self.to_date_label)
        from_to_layout.addWidget(self.to_date_edit)
        custom_time_layout.addWidget(self.custom_radio_button)
        custom_time_layout.addLayout(from_to_layout)
        custom_time_layout.addStretch()
        main_layout.addLayout(standard_time_layout)
        main_layout.addLayout(custom_time_layout)
        date_options_group_box.setLayout(main_layout)
        return date_options_group_box

    def _create_total_group(self) -> QGroupBox:
        total_group_box = QGroupBox()
        main_layout = QHBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        self.total_count_label = QLabel()
        self.total_value_label = QLabel()
        main_layout.addWidget(self.total_count_label)
        main_layout.addStretch()
        main_layout.addWidget(self.total_value_label)
        total_group_box.setLayout(main_layout)
        return total_group_box

    def _setup_date_edits(self) -> None:
        date_edits = [self.from_date_edit, self.to_date_edit]
        for date_edit in date_edits:
            calendar = date_edit.calendarWidget()
            if calendar:
                calendar.setMinimumWidth(250)
                calendar.setMinimumHeight(200)
        today = QDate.currentDate()
        minimum_date = QDate(2026, 1, 1)
        self.from_date_edit.setMinimumDate(minimum_date)
        self.from_date_edit.setMaximumDate(today)
        self.from_date_edit.setDate(today)
        self.to_date_edit.setMinimumDate(minimum_date)
        self.to_date_edit.setMaximumDate(today)
        self.to_date_edit.setDate(today)

    def _apply_date_state(self) -> None:
        if self.custom_radio_button.isChecked():
            self.from_date_edit.setEnabled(True)
            self.to_date_edit.setEnabled(True)
        else:
            self.from_date_edit.setEnabled(False)
            self.to_date_edit.setEnabled(False)

    def _update_to_date_minimum(self, date: QDate) -> None:
        self.to_date_edit.setMinimumDate(date)

    def _update_from_date_maximum(self, date: QDate) -> None:
        self.from_date_edit.setMaximumDate(date)

    def set_info_text(self, commodity: str) -> None:
        self.info_label.setText(commodity)

    def set_count_text(self, total_count: int) -> None:
        self.total_count_label.setText(f"{self.count_text} {total_count}")

    def set_value_text(self, value: float, unit: str) -> None:
        self.total_value_label.setText(f"{self.value_text} {value} {unit}")

    def _get_date_interval(self) -> tuple[str, str]:
        date_map = {
            self.today_radio_button: "today",
            self.week_radio_button: "week",
            self.month_radio_button: "month",
            self.year_radio_button: "year",
        }
        for key, value in date_map.items():
            if key.isChecked():
                date_range = get_filter_range(value)
                if date_range is not None:
                    return date_range
        date_range = (
            format_date_to_utc(self.from_date_edit.date()),
            format_date_to_utc(self.to_date_edit.date(), True),
        )
        return date_range

    def get_date_range(self) -> tuple[str, str]:
        return self._get_date_interval()

    def reload_history_data(self, history_data: list[list[str | float]]) -> None:
        self.inventory_history_model.load_data(history_data)
