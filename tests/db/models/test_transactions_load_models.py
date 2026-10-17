import uuid

import pytest
from PySide6.QtSql import QSqlDatabase

from material_register.db.models.transactions_models.transactions_load_model_in import (
    TransactionsLoadModelIn,
)
from material_register.db.models.transactions_models.transactions_load_model_out import (
    TransactionsLoadModelOut,
)
from material_register.db.queries.transactions_load_queries import (
    TransactionsLoadQueries,
)
from material_register.domain.transaction_dataclass import Transaction


@pytest.fixture
def connection() -> QSqlDatabase:
    connection_name = f"test_transactions_load_model_{uuid.uuid4().hex}"
    db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    db.setDatabaseName(":memory:")
    db.open()
    return db


@pytest.mark.parametrize(
    ("model_class", "query_method"),
    [
        (TransactionsLoadModelIn, "load_transaction_in"),
        (TransactionsLoadModelOut, "load_transactions_out"),
    ],
)
def test_load_transactions_data_updates_model_on_success(
    connection: QSqlDatabase, monkeypatch, model_class, query_method: str
) -> None:
    transaction = Transaction(transaction_id=1)
    monkeypatch.setattr(
        TransactionsLoadQueries,
        query_method,
        lambda db_connection: (True, "", [transaction]),
    )
    model = model_class(connection)
    ok, error = model.load_transactions_data()
    assert ok is True
    assert error == ""
    assert model.transaction_data == [transaction]
    assert model.total_count == 1


@pytest.mark.parametrize(
    ("model_class", "query_method"),
    [
        (TransactionsLoadModelIn, "load_transaction_in"),
        (TransactionsLoadModelOut, "load_transactions_out"),
    ],
)
def test_load_transactions_data_clears_model_on_successful_empty_result(
    connection: QSqlDatabase, monkeypatch, model_class, query_method: str
) -> None:
    monkeypatch.setattr(
        TransactionsLoadQueries,
        query_method,
        lambda db_connection: (True, "", []),
    )
    model = model_class(connection)
    model.transaction_data = [Transaction(transaction_id=1)]
    model.total_count = 1
    ok, error = model.load_transactions_data()
    assert ok is True
    assert error == ""
    assert model.transaction_data == []
    assert model.total_count == 0


@pytest.mark.parametrize(
    ("model_class", "query_method"),
    [
        (TransactionsLoadModelIn, "load_transaction_in"),
        (TransactionsLoadModelOut, "load_transactions_out"),
    ],
)
def test_load_transactions_data_preserves_model_on_query_error(
    connection: QSqlDatabase, monkeypatch, model_class, query_method: str
) -> None:
    transaction = Transaction(transaction_id=1)
    monkeypatch.setattr(
        TransactionsLoadQueries,
        query_method,
        lambda db_connection: (False, "query failed", []),
    )
    model = model_class(connection)
    model.transaction_data = [transaction]
    model.total_count = 1
    ok, error = model.load_transactions_data()
    assert ok is False
    assert error == "query failed"
    assert model.transaction_data == [transaction]
    assert model.total_count == 1
