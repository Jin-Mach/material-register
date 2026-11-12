import pytest
from PySide6.QtGui import QStandardItemModel

from material_register.controllers.transactions_controller import (
    TransactionsController,
)
from material_register.db.models.transactions_models.transaction_items_model_out import (
    TransactionItemsModelOut,
)
from material_register.ui.config.ui_constants import (
    PAYMENT_CASH,
    PAYMENT_TRANSFER,
    TRANSFER_IN,
    TRANSFER_OUT,
)


@pytest.fixture
def model() -> TransactionItemsModelOut:
    return TransactionItemsModelOut()


@pytest.fixture
def item() -> dict[str, str | int | float]:
    return {
        "category": "Food",
        "commodity": "Apple",
        "commodityId": 1,
        "unitCount": 2.0,
        "pricePerUnit": 10,
        "commoditySuffix": "kg",
    }


@pytest.mark.parametrize(
    "data",
    [
        None,
        {},
        {"value": None},
        {"value": ""},
    ],
)
def test_check_data_invalid(
    data: dict[str, str | int | float | None] | None,
) -> None:
    assert TransactionsController._check_data(data) is False


@pytest.mark.parametrize(
    "data",
    [
        {"value": "valid"},
        {"value": 1},
        {"value": 0},
    ],
)
def test_check_data_valid(data: dict[str, str | int | float]) -> None:
    assert TransactionsController._check_data(data) is True


@pytest.mark.parametrize(
    "key, value",
    [
        ("transaction_type", None),
        ("transaction_type", ""),
        ("customer_id", None),
        ("customer_id", ""),
        ("is_invoiced", None),
        ("is_invoiced", ""),
    ],
)
def test_is_dialog_data_valid_required_data_invalid(
    key: str, value: str | int | None
) -> None:
    data = {
        "transaction_type": TRANSFER_IN,
        "customer_id": 1,
        "payment_type": PAYMENT_CASH,
        "is_invoiced": False,
        "notes": None,
    }
    data[key] = value
    assert TransactionsController._is_dialog_data_valid(data, TRANSFER_IN) is False


@pytest.mark.parametrize("notes", [None, ""])
def test_is_dialog_data_valid_optional_notes(notes: str | None) -> None:
    data = {
        "transaction_type": TRANSFER_IN,
        "customer_id": 1,
        "payment_type": PAYMENT_CASH,
        "is_invoiced": False,
        "notes": notes,
    }
    assert TransactionsController._is_dialog_data_valid(data, TRANSFER_IN) is True


@pytest.mark.parametrize(
    "payment_type",
    [PAYMENT_CASH, PAYMENT_TRANSFER, None],
)
def test_is_dialog_data_valid_payment_type_in_valid(payment_type: str) -> None:
    data = {
        "transaction_type": TRANSFER_IN,
        "customer_id": 1,
        "payment_type": payment_type,
        "is_invoiced": False,
        "notes": None,
    }
    assert TransactionsController._is_dialog_data_valid(data, TRANSFER_IN) is True


@pytest.mark.parametrize("payment_type", ["INVALID", ""])
def test_is_dialog_data_valid_payment_type_in_invalid(payment_type: str) -> None:
    data = {
        "transaction_type": TRANSFER_IN,
        "customer_id": 1,
        "payment_type": payment_type,
        "is_invoiced": False,
        "notes": None,
    }
    assert TransactionsController._is_dialog_data_valid(data, TRANSFER_IN) is False


@pytest.mark.parametrize("payment_type", [None, "", "INVALID"])
def test_is_dialog_data_valid_payment_type_out_ignored(
    payment_type: str | None,
) -> None:
    data = {
        "transaction_type": TRANSFER_OUT,
        "customer_id": 1,
        "payment_type": payment_type,
        "is_invoiced": False,
        "notes": None,
    }
    assert TransactionsController._is_dialog_data_valid(data, TRANSFER_OUT) is True


def test_check_transaction_data_invalid_dialog_data(
    model: TransactionItemsModelOut,
) -> None:
    data = {
        "transaction_type": TRANSFER_IN,
        "customer_id": 1,
        "payment_type": "INVALID",
        "is_invoiced": False,
        "notes": None,
    }
    assert (
        TransactionsController._check_transaction_data(data, model, TRANSFER_IN)
        is False
    )


def test_check_transaction_data_invalid_model() -> None:
    data = {
        "transaction_type": TRANSFER_OUT,
        "customer_id": 1,
        "payment_type": None,
        "is_invoiced": False,
        "notes": None,
    }
    assert (
        TransactionsController._check_transaction_data(
            data, QStandardItemModel(), TRANSFER_OUT
        )
        is False
    )


def test_check_transaction_data_empty_model(
    model: TransactionItemsModelOut,
) -> None:
    data = {
        "transaction_type": TRANSFER_OUT,
        "customer_id": 1,
        "payment_type": None,
        "is_invoiced": False,
        "notes": None,
    }
    assert (
        TransactionsController._check_transaction_data(data, model, TRANSFER_OUT)
        is False
    )


def test_check_transaction_data_valid(
    model: TransactionItemsModelOut,
    item: dict[str, str | int | float],
) -> None:
    model.add_item(item)
    data = {
        "transaction_type": TRANSFER_OUT,
        "customer_id": 1,
        "payment_type": None,
        "is_invoiced": False,
        "notes": None,
    }
    assert (
        TransactionsController._check_transaction_data(data, model, TRANSFER_OUT)
        is True
    )
