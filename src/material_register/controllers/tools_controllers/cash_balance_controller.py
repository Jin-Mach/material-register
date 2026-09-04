from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox

from material_register.db.queries.transactions_queries import TransactionsQueries
from material_register.init.db_init import DbInit
from material_register.providers.settings_provider import SettingsProvider
from material_register.utils.date_filters import get_filter_range

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.cash_balance_widget import (
        CashBalanceWidget,
    )


class CashBalanceController:
    def __init__(self, cash_balance_widget: "CashBalanceWidget") -> None:
        self.cash_balance_widget = cash_balance_widget

    def load_balance_value(self) -> None:
        balance = 0.0
        if CashBalanceController._get_user_setting("balanceCashCheckbox", default=True):
            balance = (
                SettingsProvider.SETTINGS.get("export", {})
                .get("summary", {})
                .get("user", {})
                .get("openingBalanceSpinbox", 0.0)
            )
        self.cash_balance_widget.opening_balance_spinbox.setValue(balance)

    @staticmethod
    def load_cash_values(cash_map: dict[str, QSpinBox | QDoubleSpinBox]) -> None:
        cash = (
            SettingsProvider.SETTINGS.get("tools", {})
            .get("cash_balance_values", {})
            .get("user", {})
        )
        if cash:
            for key, spinbox in cash_map.items():
                spinbox.setValue(cash.get(key, 0))

    @staticmethod
    def load_transactions_value(transactions_spinbox: QDoubleSpinBox) -> None:
        from_date, to_date = get_filter_range("today")
        transactions_value = TransactionsQueries.get_total_price(
            DbInit.db_connection, from_date, to_date
        )
        transactions_spinbox.setValue(transactions_value)

    @staticmethod
    def update_cash_balance_values(values: list[str]) -> None:
        SettingsProvider.update_settings_sections(
            "tools", "cash_balance_values", values
        )

    @staticmethod
    def save_balance_values(
        values: dict[str, int | float],
        values_save: bool = True,
        others_save: bool = False,
    ) -> None:
        for key, value in values.items():
            if key == "othersLabel":
                if not others_save:
                    value = 0.0
            elif not values_save:
                value = 0
            SettingsProvider.SETTINGS["tools"]["cash_balance_values"]["user"][key] = (
                value
            )

    @staticmethod
    def _get_user_setting(key: str, default: bool = False) -> bool:
        return (
            SettingsProvider.SETTINGS.get("tools", {})
            .get("settings", {})
            .get("user", {})
            .get(key, default)
        )
