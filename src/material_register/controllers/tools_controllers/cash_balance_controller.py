from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDoubleSpinBox, QSpinBox

from material_register.providers.settings_provider import SettingsProvider

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.cash_balance_widget import (
        CashBalanceWidget,
    )


class CashBalanceController:
    def __init__(self, cash_balance_widget: "CashBalanceWidget") -> None:
        self.cash_balance_widget = cash_balance_widget

    def load_balance_value(self) -> None:
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
    def update_cash_balance_values(values: list[str]) -> None:
        SettingsProvider.update_settings_sections(
            "tools", "cash_balance_values", values
        )

    @staticmethod
    def save_balance_values(values: dict[str, int | float]) -> None:
        for key, value in values.items():
            SettingsProvider.SETTINGS["tools"]["cash_balance_values"]["user"][key] = (
                value
            )
