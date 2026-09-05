import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.export_queries.summary_export_queries import (
    SummaryExportQueries,
)


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE", "summary_export_test")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


@pytest.fixture
def schema(connection) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    query.exec("""
        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY,
            name TEXT,
            category_id INTEGER,
            unit TEXT
        )
    """)
    query.exec("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            type TEXT,
            created_at TEXT,
            payment_type TEXT,
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


def test_load_export_data_in(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO categories VALUES (1, 'Fe')")
    query.exec("INSERT INTO commodities VALUES (1, 'Fe 12345', 1, 'kg')")
    query.exec("""
        INSERT INTO transactions VALUES 
        (1, 'IN', '2026-07-25 08:00:00', 'CASH', NULL)
    """)
    query.exec("""
        INSERT INTO transactions VALUES 
        (2, 'IN', '2026-07-25 09:00:00', 'TRANSFER', NULL)
    """)
    query.exec("""
        INSERT INTO transaction_items VALUES
        (1, 1, 1, 100, 3.5)
    """)
    query.exec("""
        INSERT INTO transaction_items VALUES
        (2, 2, 1, 50, 3.5)
    """)
    ok, error, results = SummaryExportQueries.load_export_data_in(
        connection, "2026-07-25 08:00:00", "2026-07-25 09:00:00"
    )
    assert ok == True
    assert error == ""
    assert len(results) == 2
    assert results[0].category_name == "Fe"
    assert results[0].payment_type == "CASH"
    assert results[0].commodity_name == "Fe 12345"
    assert results[0].commodity_unit == "kg"
    assert results[0].price_per_unit == 3.5
    assert results[0].total_quantity == 100
    assert results[0].total_price == 350
    assert results[1].category_name == "Fe"
    assert results[1].payment_type == "TRANSFER"
    assert results[1].commodity_name == "Fe 12345"
    assert results[1].commodity_unit == "kg"
    assert results[1].price_per_unit == 3.5
    assert results[1].total_quantity == 50
    assert results[1].total_price == 175


def test_load_export_data_out(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("INSERT INTO categories VALUES (1, 'Fe')")
    query.exec("INSERT INTO commodities VALUES (1, 'Fe 12345', 1, 'kg')")
    query.exec("""
        INSERT INTO transactions VALUES 
        (1, 'OUT', '2026-07-25 08:00:00', NULL, NULL)
    """)
    query.exec("""
        INSERT INTO transactions VALUES 
        (2, 'OUT', '2026-07-25 09:00:00', NULL, NULL)
    """)
    query.exec("""
        INSERT INTO transaction_items VALUES
        (1, 1, 1, 100, 3.5)
    """)
    query.exec("""
        INSERT INTO transaction_items VALUES
        (2, 2, 1, 50, 4.0)
    """)
    ok, error, results = SummaryExportQueries.load_export_data_out(
        connection, "2026-07-25 08:00:00", "2026-07-25 09:00:00"
    )
    assert ok == True
    assert error == ""
    assert len(results) == 1
    assert results[0].category_name == "Fe"
    assert results[0].commodity_name == "Fe 12345"
    assert results[0].commodity_unit == "kg"
    assert results[0].total_quantity == 150
