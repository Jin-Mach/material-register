import uuid
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.inventory_history_queries import (
    InventoryHistoryQueries,
)


@pytest.fixture
def connection() -> QSqlDatabase:
    connection_name = f"test_inventory_history_queries_{uuid.uuid4().hex}"
    conn = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


@pytest.fixture
def schema(connection: QSqlDatabase) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY,
            type TEXT,
            created_at TEXT
        )
    """)
    query.exec("""
        CREATE TABLE transaction_items (
            id INTEGER PRIMARY KEY,
            transaction_id INTEGER,
            commodity_id INTEGER,
            unit_count REAL
        )
    """)


def test_get_inventory_history_data(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (id, type, created_at)
        VALUES
            (1, 'IN', '2025-01-01 10:00:00'),
            (2, 'OUT', '2025-01-01 15:00:00'),
            (3, 'IN', '2025-01-02 10:00:00'),
            (4, 'OUT', '2025-01-02 15:00:00')
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count)
        VALUES
            (1, 1, 1, 10),
            (2, 2, 1, 3),
            (3, 3, 1, 5),
            (4, 4, 1, 2),
            (5, 3, 2, 100)
    """)
    success, data = InventoryHistoryQueries.get_inventory_history_data(
        connection,
        1,
        "2025-01-01 00:00:00",
        "2025-01-02 23:59:59",
    )
    assert success is True
    assert data == [
        ["2025-01-01", 7],
        ["2025-01-02", 3],
    ]


def test_get_inventory_history_data_respects_commodity_and_interval(
    connection: QSqlDatabase, schema
) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (id, type, created_at)
        VALUES
            (1, 'IN', '2025-01-01 10:00:00'),
            (2, 'IN', '2025-01-10 10:00:00'),
            (3, 'OUT', '2025-01-15 10:00:00')
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count)
        VALUES
            (1, 1, 1, 10),
            (2, 2, 1, 20),
            (3, 3, 2, 5)
    """)
    success, data = InventoryHistoryQueries.get_inventory_history_data(
        connection,
        1,
        "2025-01-05 00:00:00",
        "2025-01-12 23:59:59",
    )
    assert success is True
    assert data == [["2025-01-10", 20]]


def test_get_inventory_history_data_returns_empty_results(
    connection: QSqlDatabase, schema
) -> None:
    success, data = InventoryHistoryQueries.get_inventory_history_data(
        connection,
        1,
        "2025-01-01 00:00:00",
        "2025-01-31 23:59:59",
    )
    assert success is True
    assert data == []


def test_get_inventory_history_total(connection: QSqlDatabase, schema) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (id, type, created_at)
        VALUES
            (1, 'IN', '2025-01-01 10:00:00'),
            (2, 'IN', '2025-01-02 10:00:00'),
            (3, 'OUT', '2025-01-03 10:00:00')
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count)
        VALUES
            (1, 1, 1, 10),
            (2, 2, 1, 5),
            (3, 3, 1, 4),
            (4, 1, 2, 100)
    """)
    success, total = InventoryHistoryQueries.get_inventory_history_total(
        connection,
        1,
        "2025-01-01 00:00:00",
        "2025-01-31 23:59:59",
    )
    assert success is True
    assert total == 11


def test_get_inventory_history_total_respects_commodity_and_interval(
    connection: QSqlDatabase, schema
) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO transactions (id, type, created_at)
        VALUES
            (1, 'IN', '2025-01-01 10:00:00'),
            (2, 'OUT', '2025-01-10 10:00:00'),
            (3, 'IN', '2025-02-01 10:00:00')
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count)
        VALUES
            (1, 1, 1, 10),
            (2, 2, 1, 3),
            (3, 3, 1, 50),
            (4, 3, 2, 100)
    """)
    success, total = InventoryHistoryQueries.get_inventory_history_total(
        connection,
        1,
        "2025-01-05 00:00:00",
        "2025-01-31 23:59:59",
    )
    assert success is True
    assert total == -3


def test_get_inventory_history_total_returns_zero(
    connection: QSqlDatabase, schema
) -> None:
    success, total = InventoryHistoryQueries.get_inventory_history_total(
        connection,
        1,
        "2025-01-01 00:00:00",
        "2025-01-31 23:59:59",
    )
    assert success is True
    assert total == 0


def test_get_inventory_history_data_groups_by_local_date(
    connection: QSqlDatabase, schema
) -> None:
    prague_tz = ZoneInfo("Europe/Prague")
    local_midnight = datetime.now(prague_tz).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    utc_before = (local_midnight - timedelta(minutes=30)).astimezone(UTC)
    utc_after = (local_midnight + timedelta(minutes=30)).astimezone(UTC)
    query = QSqlQuery(connection)
    query.exec(f"""
        INSERT INTO transactions (id, type, created_at)
        VALUES
            (1, 'IN', '{utc_before.strftime("%Y-%m-%d %H:%M:%S")}'),
            (2, 'IN', '{utc_after.strftime("%Y-%m-%d %H:%M:%S")}')
    """)
    query.exec("""
        INSERT INTO transaction_items
            (id, transaction_id, commodity_id, unit_count)
        VALUES
            (1, 1, 1, 5),
            (2, 2, 1, 3)
    """)
    start = (local_midnight - timedelta(hours=1)).astimezone(UTC)
    end = (local_midnight + timedelta(hours=1)).astimezone(UTC)
    success, data = InventoryHistoryQueries.get_inventory_history_data(
        connection,
        1,
        start.strftime("%Y-%m-%d %H:%M:%S"),
        end.strftime("%Y-%m-%d %H:%M:%S"),
    )
    assert success is True
    assert data == [
        [(local_midnight - timedelta(days=1)).strftime("%Y-%m-%d"), 5],
        [local_midnight.strftime("%Y-%m-%d"), 3],
    ]
