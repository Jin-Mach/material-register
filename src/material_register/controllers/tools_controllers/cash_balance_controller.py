from typing import TYPE_CHECKING

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

    def initialize_cash_settings(self) -> None:
        default = {}
        for value in self.cash_balance_widget.values_items:
            default[value] = 0
        user = SettingsProvider.SETTINGS.get("tools", {}).get("user", {})
