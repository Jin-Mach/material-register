import pytest

from material_register.ui.tools.right_toolbar_widgets.cash_balance_widget import (
    CashBalanceWidget,
)


@pytest.mark.parametrize(
    "opening_balance, transactions_cash, income, expense, result",
    [
        (1000.0, 500.0, 200, 100, 600),
        (-1000, 500, 200, 100, -1400),
        (1000.1, 500.2, 100, 100, 499.9),
    ],
    ids=["positive balance", "negative balance", "decimals"],
)
def test_calculate_balance(
    opening_balance, transactions_cash, income, expense, result
) -> None:
    assert (
        CashBalanceWidget._calculate_balance(
            opening_balance, transactions_cash, income, expense
        )
        == result
    )
