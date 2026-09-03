from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from material_register.config.ui_constants import (
    CASH_BALANCE_MAX_VALUE,
    CASH_BALANCE_MIN_VALUE,
    CASH_BALANCE_NEGATIVE_MIN_VALUE,
)
from material_register.controllers.tools_controllers.cash_balance_controller import (
    CashBalanceController,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.helpers.styles import WARNING_STYLE
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widget import RightToolbarWidget


class CashBalanceWidget(QWidget):
    def __init__(self, right_tool_bar_widget: "RightToolbarWidget") -> None:
        super().__init__(right_tool_bar_widget)
        self.cash_balance_controller = CashBalanceController(self)
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        total_layout = QVBoxLayout()
        total_layout.setContentsMargins(0, 5, 0, 0)
        total_layout.setSpacing(5)
        self.total_label = QLabel()
        self.total_label.setObjectName("totalLabel")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.total_label_value = QLabel()
        self.total_label_value.setObjectName("totalLabelValue")
        self.total_label_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_layout.addWidget(self.total_label)
        total_layout.addWidget(self.total_label_value)
        self.tab_widget = QTabWidget()
        self.cash_tab = self._create_balance_widget()
        self.cash_tab.setObjectName("cashTab")
        self.values_tab = QWidget()
        self.values_tab.setObjectName("valuesTab")
        self.tab_widget.addTab(self.cash_tab, "")
        self.tab_widget.addTab(self.values_tab, "")
        main_layout.addLayout(total_layout)
        main_layout.addWidget(self.tab_widget)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._create_values_layout(self.values_items, self.others_label_text)
        self._setup_specific_texts()
        self._setup_spinboxes()
        self._create_connections()
        self._setup_values()

    def _create_balance_widget(self) -> QWidget:
        balance_widget = QWidget()
        balance_layout = QVBoxLayout()
        balance_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        cash_layout = QFormLayout()
        self.opening_balance_label = QLabel()
        self.opening_balance_label.setObjectName("openingBalanceLabel")
        self.opening_balance_spinbox = QDoubleSpinBox()
        self.opening_balance_spinbox.setObjectName("openingBalanceSpinbox")
        self.transaction_cash_label = QLabel()
        self.transaction_cash_label.setObjectName("transactionCashLabel")
        self.transaction_cash_spinbox = QDoubleSpinBox()
        self.transaction_cash_spinbox.setObjectName("transactionCashSpinbox")
        self.income_label = QLabel()
        self.income_label.setObjectName("incomeLabel")
        self.income_spinbox = QDoubleSpinBox()
        self.income_spinbox.setObjectName("incomeSpinbox")
        self.expense_label = QLabel()
        self.expense_label.setObjectName("expenseLabel")
        self.expense_spinbox = QDoubleSpinBox()
        self.expense_spinbox.setObjectName("expenseSpinbox")
        self.balance_count_label = QLabel()
        self.balance_count_label.setObjectName("balanceCountLabel")
        self.balance_count_spinbox = QDoubleSpinBox()
        self.balance_count_spinbox.setObjectName("balanceCountSpinbox")
        cash_layout.addRow(self.opening_balance_label, self.opening_balance_spinbox)
        cash_layout.addRow(self.transaction_cash_label, self.transaction_cash_spinbox)
        cash_layout.addRow(self.income_label, self.income_spinbox)
        cash_layout.addRow(self.expense_label, self.expense_spinbox)
        cash_layout.addRow(self.balance_count_label, self.balance_count_spinbox)
        balance_layout.addLayout(cash_layout)
        balance_layout.addStretch()
        balance_widget.setLayout(balance_layout)
        return balance_widget

    def _create_values_layout(
        self, values_items: list[str], others_label_text: str
    ) -> None:
        self.values_spinboxes = {}
        values_layout = QVBoxLayout()
        cash_layout = QFormLayout()
        for item in values_items:
            label = QLabel(item)
            value_spinbox = QSpinBox()
            value_spinbox.setMinimum(CASH_BALANCE_MIN_VALUE)
            value_spinbox.setMaximum(CASH_BALANCE_MAX_VALUE)
            value_spinbox.setGroupSeparatorShown(True)
            cash_layout.addRow(label, value_spinbox)
            self.values_spinboxes[item] = value_spinbox
        self.others_label = QLabel()
        self.others_label.setObjectName("othersLabel")
        self.others_label.setText(others_label_text)
        self.others_spinbox = QDoubleSpinBox()
        self.others_spinbox.setObjectName("othersSpinbox")
        cash_layout.addRow(self.others_label, self.others_spinbox)
        self.cash_total_label = QLabel()
        self.cash_total_label.setObjectName("cashTotalLabel")
        self.cash_total_spinbox = QDoubleSpinBox()
        self.cash_total_spinbox.setObjectName("cashTotalSpinbox")
        cash_layout.addRow(self.cash_total_label, self.cash_total_spinbox)
        values_layout.addLayout(cash_layout)
        values_layout.addStretch()
        self.values_tab.setLayout(values_layout)

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        ui_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        self.cash_tab_text = ui_texts.get("cashTabText", "Income and expenses")
        self.values_tab_text = ui_texts.get("valuesTabText", "Cash")
        self.values_items = ui_texts.get("valueItems", [])
        self.others_label_text = ui_texts.get("othersLabelText", "Other:")
        self.cash_total_label_text = ui_texts.get("cashTotalLabelText", "Total:")
        self.total_label_text = ui_texts.get("totalLabelText", "Difference:")
        self.currency_suffix = ui_texts.get("currencySuffix", "")
        self.quantity_suffix = ui_texts.get("quantitySuffix", "")
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, widgets):
            return

    def _setup_specific_texts(self) -> None:
        self.tab_widget.setTabText(0, self.cash_tab_text)
        self.tab_widget.setTabText(1, self.values_tab_text)
        self.total_label.setText(self.total_label_text)
        self.total_label_value.setText(f"0 {self.currency_suffix}")
        self.cash_total_label.setText(self.cash_total_label_text)

    def _setup_values(self) -> None:
        values = self.values_items + [self.others_label.objectName()]
        self.cash_balance_controller.update_cash_balance_values(values)
        self.cash_balance_controller.load_balance_value()
        cash_map = self.values_spinboxes.copy()
        cash_map[self.others_label.objectName()] = self.others_spinbox
        self.cash_balance_controller.load_cash_values(cash_map)
        self.cash_balance_controller.load_transactions_value(
            self.transaction_cash_spinbox
        )
        self.update_totals()

    def _create_connections(self) -> None:
        spinboxes = [
            self.opening_balance_spinbox,
            self.income_spinbox,
            self.expense_spinbox,
            self.others_spinbox,
        ]
        spinboxes += list(self.values_spinboxes.values())
        for spinbox in spinboxes:
            spinbox.valueChanged.connect(self.update_totals)

    def update_totals(self) -> None:
        balance = CashBalanceWidget._calculate_balance(
            self.opening_balance_spinbox.value(),
            self.transaction_cash_spinbox.value(),
            self.income_spinbox.value(),
            self.expense_spinbox.value(),
        )
        cash_total = self._calculate_cash_total()
        total = round(cash_total - balance, 1)
        self.balance_count_spinbox.setValue(balance)
        self.cash_total_spinbox.setValue(cash_total)
        if total != 0:
            self.total_label_value.setStyleSheet(WARNING_STYLE)
        else:
            self.total_label_value.setStyleSheet("")
        total_text = f"{total:.1f}".replace(".", self.decimal)
        self.total_label_value.setText(f"{total_text} {self.currency_suffix}")

    def _setup_spinboxes(self) -> None:
        disabled_spinboxes = [
            self.balance_count_spinbox,
            self.transaction_cash_spinbox,
            self.cash_total_spinbox,
        ]
        decimal_spinboxes = [
            self.opening_balance_spinbox,
            self.transaction_cash_spinbox,
            self.income_spinbox,
            self.expense_spinbox,
            self.balance_count_spinbox,
            self.cash_total_spinbox,
            self.others_spinbox,
        ]
        for spinbox in disabled_spinboxes:
            spinbox.setDisabled(True)
        for spinbox in decimal_spinboxes:
            spinbox.setDecimals(1)
            spinbox.setSingleStep(1)
            spinbox.setMinimum(CASH_BALANCE_MIN_VALUE)
            spinbox.setMaximum(CASH_BALANCE_MAX_VALUE)
        self.opening_balance_spinbox.setMinimum(CASH_BALANCE_NEGATIVE_MIN_VALUE)
        self.balance_count_spinbox.setMinimum(CASH_BALANCE_NEGATIVE_MIN_VALUE)
        for spinbox in self.findChildren(QSpinBox):
            spinbox.setGroupSeparatorShown(True)
        for spinbox in self.findChildren(QDoubleSpinBox):
            spinbox.setGroupSeparatorShown(True)
        for spinbox in decimal_spinboxes:
            spinbox.setSuffix(self.currency_suffix)
        for spinbox in self.values_spinboxes.values():
            spinbox.setSuffix(self.quantity_suffix)
        locale = self.opening_balance_spinbox.locale()
        self.decimal = locale.decimalPoint()

    def _calculate_cash_total(self) -> float:
        cash_total = sum(
            float(value) * spinbox.value()
            for value, spinbox in self.values_spinboxes.items()
        )
        return round(cash_total + self.others_spinbox.value(), 1)

    @staticmethod
    def _calculate_balance(
        opening_balance: float,
        transaction_cash: float,
        income: float,
        expense: float,
    ) -> float:
        return round(opening_balance - transaction_cash + income - expense, 1)

    def get_values_map(self) -> dict[str, int | float]:
        values_map = {}
        values = self.values_spinboxes.copy()
        values[self.others_label.objectName()] = self.others_spinbox
        for key, spinbox in values.items():
            value = spinbox.value()
            values_map[key] = value
        return values_map
