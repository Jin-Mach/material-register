import pytest
from PySide6.QtCore import Qt

from material_register.db.config.model_constants import (
    SEARCH_MODEL_COLUMNS,
    SEARCH_MODEL_COLUMNS_MAP,
)
from material_register.db.models.search_models.search_transactions_model import (
    SearchTransactionsModel,
)
from material_register.domain.search_dataclass import SearchDataclass
from material_register.ui.config.ui_constants import TRANSFER_IN, TRANSFER_OUT


@pytest.fixture
def model() -> SearchTransactionsModel:
    return SearchTransactionsModel()


@pytest.fixture
def transaction_in() -> SearchDataclass:
    return SearchDataclass(
        transaction_id=1,
        transaction_type=TRANSFER_IN,
        transaction_created_at="2026-10-01 10:30:00",
        customer_name="John Smith",
        customer_document_number="INV-001",
        customer_address="London",
        total=100.0,
    )


@pytest.fixture
def transaction_out() -> SearchDataclass:
    return SearchDataclass(
        transaction_id=2,
        transaction_type=TRANSFER_OUT,
        transaction_created_at="2026-10-02 12:00:00",
        customer_name="Jane Smith",
        customer_document_number="INV-002",
        customer_address="Manchester",
        total=50.0,
        suffix="kg",
    )


def test_load_data(
    model: SearchTransactionsModel,
    transaction_in: SearchDataclass,
    transaction_out: SearchDataclass,
) -> None:
    model.load_data([transaction_in, transaction_out])
    assert model.rowCount() == 2
    assert model.columnCount() == len(SEARCH_MODEL_COLUMNS)
    assert model.total_count == 2


def test_get_columns_map() -> None:
    assert SearchTransactionsModel.get_columns_map() == SEARCH_MODEL_COLUMNS_MAP


def test_display_transaction_data(
    model: SearchTransactionsModel, transaction_in: SearchDataclass
) -> None:
    model.set_transaction_type_texts("IN", "OUT")
    model.load_data([transaction_in])
    index_id = model.index(0, SEARCH_MODEL_COLUMNS_MAP["transaction_id"])
    assert model.data(index_id, Qt.ItemDataRole.DisplayRole) == 1
    index_type = model.index(0, SEARCH_MODEL_COLUMNS_MAP["transaction_type"])
    assert model.data(index_type, Qt.ItemDataRole.DisplayRole) == TRANSFER_IN
    index_customer = model.index(0, SEARCH_MODEL_COLUMNS_MAP["customer_name"])
    assert model.data(index_customer, Qt.ItemDataRole.DisplayRole) == "John Smith"
    index_document = model.index(
        0, SEARCH_MODEL_COLUMNS_MAP["customer_document_number"]
    )
    assert model.data(index_document, Qt.ItemDataRole.DisplayRole) == "INV-001"
    index_address = model.index(0, SEARCH_MODEL_COLUMNS_MAP["customer_address"])
    assert model.data(index_address, Qt.ItemDataRole.DisplayRole) == "London"


def test_display_total_in(
    model: SearchTransactionsModel, transaction_in: SearchDataclass
) -> None:
    model.set_suffix("£")
    model.load_data([transaction_in])
    index = model.index(0, SEARCH_MODEL_COLUMNS_MAP["total"])
    assert model.data(index, Qt.ItemDataRole.DisplayRole) == "100,0 £"


def test_display_total_out(
    model: SearchTransactionsModel, transaction_out: SearchDataclass
) -> None:
    model.load_data([transaction_out])
    index = model.index(0, SEARCH_MODEL_COLUMNS_MAP["total"])
    assert model.data(index, Qt.ItemDataRole.DisplayRole) == "50,0 kg"


def test_display_transaction_date(
    model: SearchTransactionsModel, transaction_in: SearchDataclass
) -> None:
    model.load_data([transaction_in])
    index = model.index(0, SEARCH_MODEL_COLUMNS_MAP["transaction_created_at"])
    value = model.data(index, Qt.ItemDataRole.DisplayRole)
    assert value is not None
    assert value != transaction_in.transaction_created_at


def test_text_alignment(
    model: SearchTransactionsModel, transaction_in: SearchDataclass
) -> None:
    model.load_data([transaction_in])
    index_total = model.index(0, SEARCH_MODEL_COLUMNS_MAP["total"])
    assert model.data(index_total, Qt.ItemDataRole.TextAlignmentRole) == (
        Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
    )
    index_customer = model.index(0, SEARCH_MODEL_COLUMNS_MAP["customer_name"])
    assert (
        model.data(index_customer, Qt.ItemDataRole.TextAlignmentRole)
        == Qt.AlignmentFlag.AlignCenter
    )


def test_header_data(model: SearchTransactionsModel) -> None:
    model.headers = {0: "ID", 1: "Type", 2: "Date"}
    assert model.headerData(0, Qt.Orientation.Horizontal) == "ID"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Type"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Date"


def test_load_empty_data(model: SearchTransactionsModel) -> None:
    model.load_data([])
    assert model.rowCount() == 0
    assert model.total_count == 0
