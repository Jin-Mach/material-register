from PySide6.QtSql import QSqlQuery

from material_register.db.create_connection import create_connection


def test_db_is_none()-> None:
    db = create_connection(None, "test.db", "test_connection")
    assert db is None

def test_create_connection_invalid_path(tmp_path) -> None:
    invalid_dir = tmp_path / "invalid_dir" / "invalid_dir_2"
    db = create_connection(invalid_dir, "test.db", "test_connection")
    assert db is None

def test_create_connection_success(tmp_path):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    db = create_connection(db_dir, "test.db", "test_connection")
    assert db is not None
    assert (db_dir / "test.db").exists()

def test_tables_created(tmp_path):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    db = create_connection(db_dir, "test.db", "test_connection")
    assert db is not None
    query = QSqlQuery(db)
    query.exec("SELECT name FROM sqlite_master WHERE type='table'")
    tables = []
    while query.next():
        tables.append(query.value(0))
    expected = {
        "customers",
        "categories",
        "commodities",
        "inventory",
        "transactions",
        "transaction_items",
    }
    assert expected.issubset(set(tables))

def test_trigger_new_commodity(tmp_path):
    db_dir = tmp_path / "db"
    db_dir.mkdir()
    db = create_connection(db_dir, "test.db", "test_connection")
    assert db is not None
    query = QSqlQuery(db)
    query.exec("INSERT INTO categories (name) VALUES ('Fe')")
    query.exec("""
        INSERT INTO commodities (name, category_id)
        VALUES ('12345', 1)
    """)
    query.exec("SELECT stock FROM inventory WHERE commodity_id = 1")
    assert query.next()
    assert query.value(0) == 0