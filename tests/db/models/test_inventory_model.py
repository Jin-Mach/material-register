import uuid

from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.config.model_constants import INVENTORY_COLUMNS_MAP
from material_register.db.models.inventory_model import InventoryModel
from material_register.ui.setup.ui_icons import UiIcons


def _create_memory_db() -> QSqlDatabase:
    name = f"inv_test_{uuid.uuid4()}"
    db = QSqlDatabase.addDatabase("QSQLITE", name)
    db.setDatabaseName(":memory:")
    db.open()
    return db


def test_load_inventory_data_and_display_roles() -> None:
    db = _create_memory_db()
    query = QSqlQuery(db)
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
            unit TEXT,
            category_id INTEGER,
            active INTEGER
        )
    """)
    query.exec("""
        CREATE TABLE inventory (
            commodity_id INTEGER PRIMARY KEY,
            stock REAL NOT NULL
        )
    """)
    query.exec("INSERT INTO categories (id, name) VALUES (1, 'Food')")
    query.exec(
        "INSERT INTO commodities (id, name, unit, category_id, active) VALUES (1, 'Apple', 'kg', 1, 1)"
    )
    query.exec("INSERT INTO inventory (commodity_id, stock) VALUES (1, 5)")
    model = InventoryModel(db)
    ok, error = model.load_inventory_data()
    assert ok is True
    assert error == ""
    assert model.rowCount() == 1
    stock_col = INVENTORY_COLUMNS_MAP["inventory_stock"]
    active_col = INVENTORY_COLUMNS_MAP["commodity_active"]
    index_stock = model.index(0, stock_col)
    display = model.data(index_stock, Qt.ItemDataRole.DisplayRole)
    assert "kg" in display
    assert "5" in display
    index_active = model.index(0, active_col)
    deco = model.data(index_active, Qt.ItemDataRole.DecorationRole)
    assert deco == UiIcons.ACTIVE_ICON


def test_inactive_inventory_item_shows_inactive_icon() -> None:
    db = _create_memory_db()
    query = QSqlQuery(db)
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
            unit TEXT,
            category_id INTEGER,
            active INTEGER
        )
    """)
    query.exec("""
        CREATE TABLE inventory (
            commodity_id INTEGER PRIMARY KEY,
            stock REAL NOT NULL
        )
    """)
    query.exec("INSERT INTO categories (id, name) VALUES (1, 'Tools')")
    query.exec(
        "INSERT INTO commodities (id, name, unit, category_id, active) VALUES (2, 'Hammer', 'pcs', 1, 0)"
    )
    query.exec("INSERT INTO inventory (commodity_id, stock) VALUES (2, -2)")
    model = InventoryModel(db)
    ok, error = model.load_inventory_data()
    assert ok is True
    assert error == ""
    assert model.rowCount() == 1
    active_col = INVENTORY_COLUMNS_MAP["commodity_active"]
    index_active = model.index(0, active_col)
    deco = model.data(index_active, Qt.ItemDataRole.DecorationRole)
    assert deco == UiIcons.INACTIVE_ICON
