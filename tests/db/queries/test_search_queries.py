import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.search_queries import SearchQueries


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "search_test")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


@pytest.fixture
def schema(connection: QSqlDatabase) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            company TEXT,
            first_name TEXT,
            last_name TEXT,
            document_number TEXT,
            address TEXT,
            company_normalized TEXT,
            first_name_normalized TEXT,
            last_name_normalized TEXT,
            address_normalized TEXT
        )
    """)
    query.exec("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            type TEXT,
            customer_id INTEGER,
            created_at TEXT,
            payment_type TEXT,
            is_invoiced INTEGER,
            notes TEXT
        )
    """)
    query.exec("""
        CREATE TABLE transaction_items (
            id INTEGER PRIMARY KEY,
            transaction_id INTEGER,
            commodity_id INTEGER,
            unit_count REAL,
            price_per_unit REAL
        )
    """)
    query.exec("""
        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY,
            name TEXT,
            unit TEXT,
            category_id INTEGER
        )
    """)


def test_load_transactions(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'Steel', 'kg', 1)")
    query.exec("""
        INSERT INTO customers (
            id, company, first_name, last_name, document_number, address
        )
        VALUES (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars')
    """)
    query.exec("""
        INSERT INTO transactions
            (id, type, customer_id, created_at, payment_type, is_invoiced, notes)
        VALUES
            (1, 'IN', 1, '2020-01-01 10:00:00', 'TRANSFER', 0, NULL),
            (2, 'OUT', 1, '2020-01-02 10:00:00', NULL, 1, NULL)
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES
            (1, 1, 1, 10, 20),
            (2, 2, 1, 10, 20)
    """)
    success, results = SearchQueries.load_transactions(connection, "", [])
    assert success is True
    assert len(results) == 2
    transaction_in = None
    transaction_out = None
    for transaction in results:
        if transaction.transaction_type == "IN":
            transaction_in = transaction
        elif transaction.transaction_type == "OUT":
            transaction_out = transaction
    assert transaction_in.total == 200.0
    assert transaction_in.suffix is None
    assert transaction_out.total == 10.0
    assert transaction_out.suffix == "kg"
    assert transaction_out.is_invoiced is True


def test_load_transactions_includes_older_transactions(
    connection: QSqlDatabase, schema
) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'Steel', 'kg', 1)")
    query.exec("""
        INSERT INTO customers (
            id, company, first_name, last_name, document_number, address
        )
        VALUES (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars')
    """)
    query.exec("""
        INSERT INTO transactions
            (id, type, customer_id, created_at, payment_type, is_invoiced)
        VALUES
            (1, 'IN', 1, '2020-01-01 10:00:00', 'TRANSFER', 0)
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES (1, 1, 1, 10, 20)
    """)
    success, results = SearchQueries.load_transactions(connection, "", [])
    assert success is True
    assert len(results) == 1
    assert results[0].transaction_id == 1


def test_load_transactions_query_error(connection: QSqlDatabase) -> None:
    success, results = SearchQueries.load_transactions(connection, "", [])
    assert success is False
    assert results == []


def test_get_transactions_count(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (id, type)
        VALUES
            (1, 'IN'),
            (2, 'OUT'),
            (3, 'IN')
    """)
    success, transactions_count = SearchQueries.get_transactions_count(connection)
    assert success is True
    assert transactions_count == 3


def test_get_transactions_count_query_error(connection: QSqlDatabase) -> None:
    success, transactions_count = SearchQueries.get_transactions_count(connection)
    assert success is False
    assert transactions_count == 0


def test_get_total_amount(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO commodities VALUES (1, 'Steel', 'kg', 1)")
    query.exec("""
        INSERT INTO transactions (id, type)
        VALUES
            (1, 'IN'),
            (2, 'OUT'),
            (3, 'IN')
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES
            (1, 1, 1, 10, 20),
            (2, 2, 1, 10, 50),
            (3, 3, 1, 5, 30)
    """)
    success, total_amount = SearchQueries.get_total_amount(connection, "", [])
    assert success is True
    assert total_amount == 350.0


def test_get_total_amount_query_error(connection: QSqlDatabase) -> None:
    success, total_amount = SearchQueries.get_total_amount(connection, "", [])
    assert success is False
    assert total_amount == 0.0


def test_load_material(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    query.exec("""
        INSERT INTO categories VALUES
            (1, 'Metals'),
            (2, 'Plastics')
    """)
    query.exec("""
        INSERT INTO commodities VALUES
            (1, 'Steel', 'kg', 1),
            (2, 'Copper', 'kg', 1),
            (3, 'PVC', 'm', 2)
    """)
    query.exec("""
        INSERT INTO transactions (id, type)
        VALUES
            (1, 'IN'),
            (2, 'OUT'),
            (3, 'IN')
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count, price_per_unit)
        VALUES
            (1, 1, 1, 100, 20),
            (2, 2, 1, 30, 25),
            (3, 1, 2, 50, 40),
            (4, 3, 2, 20, 45),
            (5, 2, 3, 10, 15)
    """)
    success, results = SearchQueries.load_material(connection, "", [])
    assert success is True
    assert len(results) == 3
    assert results[0].category_name == "Metals"
    assert results[0].commodity_name == "Copper"
    assert results[0].commodity_unit == "kg"
    assert results[0].total == 70.0
    assert results[1].category_name == "Metals"
    assert results[1].commodity_name == "Steel"
    assert results[1].commodity_unit == "kg"
    assert results[1].total == 70.0
    assert results[2].category_name == "Plastics"
    assert results[2].commodity_name == "PVC"
    assert results[2].commodity_unit == "m"
    assert results[2].total == -10.0


def test_load_material_query_error(connection: QSqlDatabase) -> None:
    success, results = SearchQueries.load_material(connection, "", [])
    assert success is False
    assert results == []


@pytest.mark.parametrize(
    ("column", "value", "expected_ids"),
    [
        ("document_number", "ICO123", [2, 1]),
        ("company_normalized", "fake company", [2, 1]),
        ("address_normalized", "mars", [2, 1]),
        ("document_number", "ID456", [3]),
        ("first_name_normalized", "john", [3]),
        ("last_name_normalized", "doe", [3]),
        ("address_normalized", "venus", [3]),
        ("document_number", "ICO789", [4]),
        ("company_normalized", "other company", [4]),
        ("address_normalized", "jupiter", [4]),
    ],
    ids=[
        "document_number_ICO123",
        "company_fake_company",
        "address_mars",
        "document_number_ID456",
        "first_name_john",
        "last_name_doe",
        "address_venus",
        "document_number_ICO789",
        "company_other_company",
        "address_jupiter",
    ],
)
def test_load_transactions_by_customer_data(
    connection: QSqlDatabase,
    schema,
    column: str,
    value: str,
    expected_ids: list[int],
) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO customers (
            id, company, first_name, last_name, document_number, address,
            company_normalized, first_name_normalized,
            last_name_normalized, address_normalized
        )
        VALUES
            (1, 'Fake company', NULL, NULL, 'ICO123', 'Mars',
             'fake company', NULL, NULL, 'mars'),
            (2, NULL, 'John', 'Doe', 'ID456', 'Venus',
             NULL, 'john', 'doe', 'venus'),
            (3, 'Other company', NULL, NULL, 'ICO789', 'Jupiter',
             'other company', NULL, NULL, 'jupiter')
    """)
    query.exec("""
        INSERT INTO transactions
            (id, type, customer_id, created_at, payment_type, is_invoiced, notes)
        VALUES
            (1, 'IN', 1, '2020-01-01 10:00:00', 'TRANSFER', 0, NULL),
            (2, 'OUT', 1, '2020-01-02 10:00:00', NULL, 1, NULL),
            (3, 'IN', 2, '2020-01-03 10:00:00', 'TRANSFER', 0, NULL),
            (4, 'OUT', 3, '2020-01-04 10:00:00', NULL, 1, NULL)
    """)
    where = f"WHERE {column} LIKE ?"
    params = [f"%{value}%"]
    success, results = SearchQueries.load_transactions(connection, where, params)
    assert success is True
    assert len(results) == len(expected_ids)
    actual_ids = []
    for transaction in results:
        actual_ids.append(transaction.transaction_id)
    assert actual_ids == expected_ids
