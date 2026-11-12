import pytest

from material_register.controllers.tools_controllers.cash_balance_controller import (
    CashBalanceController,
)
from material_register.providers.settings_provider import SettingsProvider


@pytest.mark.parametrize(
    "values_save, others_save, expected",
    [
        (True, True, {"bill": 20, "coin": 5, "othersLabel": 3.5}),
        (False, True, {"bill": 0, "coin": 0, "othersLabel": 3.5}),
        (True, False, {"bill": 20, "coin": 5, "othersLabel": 0.0}),
        (False, False, {"bill": 0, "coin": 0, "othersLabel": 0.0}),
    ],
    ids=[
        "save-all-values",
        "save-others-only",
        "save-cash-values-only",
        "save-no-values",
    ],
)
def test_save_balance_values(
    values_save: bool, others_save: bool, expected: dict[str, int | float]
) -> None:
    original_settings = SettingsProvider.SETTINGS
    SettingsProvider.SETTINGS = {
        "tools": {
            "cash_balance_values": {"user": {"bill": 20, "coin": 5, "othersLabel": 3.5}}
        }
    }
    values = {"bill": 20, "coin": 5, "othersLabel": 3.5}
    try:
        CashBalanceController.save_balance_values(
            values, values_save=values_save, others_save=others_save
        )
        assert (
            SettingsProvider.SETTINGS["tools"]["cash_balance_values"]["user"]
            == expected
        )
    finally:
        SettingsProvider.SETTINGS = original_settings
