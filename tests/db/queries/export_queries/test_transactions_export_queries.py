import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.config.ui_constants import TRANSFER_IN, TRANSFER_OUT
from material_register.db.queries.export_queries.transactions_export_queries import (
    TransactionsExportQueries,
)


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "transactions_export_test")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


@pytest.fixture
def schema(connection) -> None:
    query = QSqlQuery(connection)
    query.exec(
        "CREATE TABLE customers (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, company TEXT, document_number TEXT, address TEXT)"
    )
    query.exec("CREATE TABLE categories (id INTEGER PRIMARY KEY, name TEXT)")
    query.exec(
        "CREATE TABLE commodities (id INTEGER PRIMARY KEY, name TEXT, category_id INTEGER, unit TEXT)"
    )
    query.exec(
        "CREATE TABLE transactions (id INTEGER PRIMARY KEY, type TEXT, customer_id INTEGER, created_at TEXT, payment_type TEXT, notes TEXT)"
    )
    query.exec(
        "CREATE TABLE transaction_items (id INTEGER PRIMARY KEY, transaction_id INTEGER, commodity_id INTEGER, unit_count REAL, price_per_unit REAL)"
    )


def test_load_export_data_in(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec(
        "INSERT INTO customers VALUES (1, 'John', 'Doe', NULL, 'DOC123', 'Some address')"
    )
    query.exec("INSERT INTO categories VALUES (1, 'Fe')")
    query.exec("INSERT INTO commodities VALUES (1, 'Fe 12345', 1, 'kg')")
    query.exec(
        "INSERT INTO transactions VALUES (1, 'IN', 1, '2026-07-25 08:00:00', 'CASH', NULL)"
    )
    query.exec(
        "INSERT INTO transactions VALUES (2, 'IN', 1, '2026-07-25 09:00:00', 'CASH', NULL)"
    )
    query.exec("INSERT INTO transaction_items VALUES (1, 1, 1, 100, 3.5)")
    query.exec("INSERT INTO transaction_items VALUES (2, 2, 1, 50, 3.5)")
    ok, error, results = TransactionsExportQueries.load_export_data(
        connection, "2026-07-25 08:00:00", "2026-07-25 09:00:00", 1, TRANSFER_IN
    )
    assert ok is True
    assert error == ""
    assert len(results) == 1
    assert results[0].transaction_date == "2026-07-25"
    assert len(results[0].transactions_list) == 2
    assert results[0].transactions_list[0].created_at == "2026-07-25 08:00:00"
    assert results[0].transactions_list[0].payment_type == "CASH"
    assert results[0].transactions_list[0].customer_name == "John Doe"
    assert results[0].transactions_list[0].document_number == "DOC123"
    assert results[0].transactions_list[0].address == "Some address"
    assert len(results[0].transactions_list[0].transaction_items) == 1
    assert results[0].transactions_list[0].transaction_items[0].category == "Fe"
    assert (
        results[0].transactions_list[0].transaction_items[0].commodity_name
        == "Fe 12345"
    )
    assert results[0].transactions_list[0].transaction_items[0].commodity_unit == "kg"
    assert results[0].transactions_list[0].transaction_items[0].unit_count == 100
    assert results[0].transactions_list[0].transaction_items[0].price_per_unit == 3.5


def test_load_export_data_out(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec(
        "INSERT INTO customers VALUES (1, 'John', 'Doe', NULL, 'DOC123', 'Some address')"
    )
    query.exec("INSERT INTO categories VALUES (1, 'Fe')")
    query.exec("INSERT INTO commodities VALUES (1, 'Fe 12345', 1, 'kg')")
    query.exec(
        "INSERT INTO transactions VALUES (1, 'OUT', 1, '2026-07-25 08:00:00', NULL, NULL)"
    )
    query.exec("INSERT INTO transaction_items VALUES (1, 1, 1, 100, 3.5)")
    ok, error, results = TransactionsExportQueries.load_export_data(
        connection, "2026-07-25 08:00:00", "2026-07-25 09:00:00", 1, TRANSFER_OUT
    )
    assert ok is True
    assert error == ""
    assert len(results) == 1
    assert results[0].transaction_date == "2026-07-25"
    assert len(results[0].transactions_list) == 1
    assert results[0].transactions_list[0].created_at == "2026-07-25 08:00:00"
    assert results[0].transactions_list[0].payment_type == ""
    assert results[0].transactions_list[0].customer_name == "John Doe"
    assert results[0].transactions_list[0].document_number == "DOC123"
    assert results[0].transactions_list[0].address == "Some address"
    assert len(results[0].transactions_list[0].transaction_items) == 1
    assert results[0].transactions_list[0].transaction_items[0].category == "Fe"
    assert (
        results[0].transactions_list[0].transaction_items[0].commodity_name
        == "Fe 12345"
    )
    assert results[0].transactions_list[0].transaction_items[0].commodity_unit == "kg"
    assert results[0].transactions_list[0].transaction_items[0].unit_count == 100
    assert results[0].transactions_list[0].transaction_items[0].price_per_unit == ""


def test_load_export_data_unknown_transfer_type(
    connection: QSqlDatabase, schema
) -> None:
    ok, error, results = TransactionsExportQueries.load_export_data(
        connection, "2026-07-25 08:00:00", "2026-07-25 09:00:00", None, "UNKNOWN"
    )
    assert ok is False
    assert error == "Unknown transfer type: UNKNOWN"
    assert results == []


def test_create_transaction(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec(
        "SELECT '2026-07-25', '2026-07-25 08:00:00', 'CASH', 'DOC123', 'Some address', 100, 3.5, 'Fe 12345', 'kg', 'Fe', 'John Doe'"
    )
    query.next()
    result = TransactionsExportQueries._create_transaction(query)
    assert result.created_at == "2026-07-25 08:00:00"
    assert result.payment_type == "CASH"
    assert result.customer_name == "John Doe"
    assert result.document_number == "DOC123"
    assert result.address == "Some address"
    assert len(result.transaction_items) == 1
    assert result.transaction_items[0].category == "Fe"
    assert result.transaction_items[0].commodity_name == "Fe 12345"
    assert result.transaction_items[0].commodity_unit == "kg"
    assert result.transaction_items[0].unit_count == 100
    assert result.transaction_items[0].price_per_unit == 3.5


def test_create_transaction_item(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec(
        "SELECT '2026-07-25', '2026-07-25 08:00:00', 'CASH', 'DOC123', 'Some address', 100, 3.5, 'Fe 12345', 'kg', 'Fe', 'John Doe'"
    )
    query.next()
    result = TransactionsExportQueries._create_transaction_item(query)
    assert result.category == "Fe"
    assert result.commodity_name == "Fe 12345"
    assert result.commodity_unit == "kg"
    assert result.unit_count == 100
    assert result.price_per_unit == 3.5
