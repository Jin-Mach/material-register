import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.commodities_queries import CommoditiesQueries
from material_register.domain.commodities_dataclass import Commodity


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase("QSQLITE")
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn


@pytest.fixture
def schema(connection) -> None:
    query = QSqlQuery(connection)
    query.exec("""
        CREATE TABLE commodities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category_id INTEGER,
            unit TEXT,
            default_price REAL,
            notes TEXT,
            active INTEGER
        )
    """)


def test_create_commodity(connection, schema) -> None:
    ok, error = CommoditiesQueries.create_commodity(
        connection, "A", 1, "kg", 10.0, "note", 1
    )
    assert ok is True
    assert error == ""
    query = QSqlQuery(connection)
    query.exec(
        "SELECT name, category_id, unit, default_price, notes, active FROM commodities"
    )
    assert query.next()
    assert query.value(0) == "A"
    assert query.value(1) == 1
    assert query.value(2) == "kg"
    assert query.value(3) == 10.0
    assert query.value(4) == "note"
    assert query.value(5) == 1


def test_update_commodity(connection, schema) -> None:
    CommoditiesQueries.create_commodity(connection, "old", 1, "kg", 5.0, "note", 1)
    query = QSqlQuery(connection)
    query.exec("SELECT id FROM commodities WHERE name='old'")
    query.next()
    commodity_id = query.value(0)
    ok, error = CommoditiesQueries.update_commodity(
        connection, commodity_id, "new", 2, "pcs", 20.0, "updated", 0
    )
    assert ok is True
    assert error == ""
    query = QSqlQuery(connection)
    query.prepare("""
        SELECT name, category_id, unit, default_price, notes, active
        FROM commodities
        WHERE id=?
    """)
    query.addBindValue(commodity_id)
    query.exec()
    assert query.next()
    assert query.value(0) == "new"
    assert query.value(1) == 2
    assert query.value(2) == "pcs"
    assert query.value(3) == 20.0
    assert query.value(4) == "updated"
    assert query.value(5) == 0


def test_change_active(connection, schema) -> None:
    CommoditiesQueries.create_commodity(connection, "A", 1, "kg", 10.0, "note", 1)
    query = QSqlQuery(connection)
    query.exec("SELECT id FROM commodities WHERE name='A'")
    query.next()
    commodity_id = query.value(0)
    ok, error = CommoditiesQueries.change_active(connection, commodity_id, 0)
    assert ok is True
    assert error == ""
    query.prepare("SELECT active FROM commodities WHERE id=?")
    query.addBindValue(commodity_id)
    query.exec()
    assert query.next()
    assert query.value(0) == 0


def test_get_commodities(connection, schema) -> None:
    CommoditiesQueries.create_commodity(connection, "A", 1, "kg", 10.0, "n1", 1)
    CommoditiesQueries.create_commodity(connection, "B", 2, "pcs", 20.0, "n2", 0)
    data = CommoditiesQueries.get_commodities(connection)
    assert len(data) == 2
    assert data == [
        Commodity(
            id=1,
            name="A",
            category_id=1,
            unit="kg",
            default_price=10.0,
            notes="n1",
            active=1,
        ),
        Commodity(
            id=2,
            name="B",
            category_id=2,
            unit="pcs",
            default_price=20.0,
            notes="n2",
            active=0,
        ),
    ]


def test_commodity_exists(connection, schema) -> None:
    CommoditiesQueries.create_commodity(connection, "A", 1, "kg", 10.0, "note", 1)
    assert CommoditiesQueries.commodity_exists(connection, "A") is True
    assert CommoditiesQueries.commodity_exists(connection, "B") is False
