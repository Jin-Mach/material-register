import uuid

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.models.customers_model import CustomersModel
from material_register.domain.customers_dataclass import Customer


def _create_test_db() -> QSqlDatabase:
    db = QSqlDatabase.addDatabase("QSQLITE", f"test_connection{uuid.uuid4()}")
    db.setDatabaseName(":memory:")
    db.open()
    query = QSqlQuery(db)
    query.exec("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        first_name TEXT,
        last_name TEXT,
        document_number TEXT,
        address TEXT,
        notes TEXT,
        created_at TEXT,
        active INTEGER DEFAULT 1,
        company_normalized TEXT,
        first_name_normalized TEXT,
        last_name_normalized TEXT,
        address_normalized TEXT
    )
    """)
    return db


def _add_customer() -> Customer:
    customer = Customer(
        company="Test s.r.o.",
        document_number="123",
        address="City",
    )
    return customer


def _update_customer() -> Customer:
    customer = Customer(
        company=" New Test s.r.o.", document_number=" New 123", address=" New City"
    )
    return customer


def test_add_customer() -> None:
    db = _create_test_db()
    model = CustomersModel(db)
    ok = model.add_customer(_add_customer())
    assert ok


def test_update_customer() -> None:
    db = _create_test_db()
    model = CustomersModel(db)
    model.add_customer(_add_customer())
    row = 0
    row_id = model.data(model.index(row, model.fieldIndex("id")))
    new_customer = _update_customer()
    ok = model.update_customer(row_id, new_customer)
    assert ok
    document_number = model.fieldIndex("document_number")
    address = model.fieldIndex("address")
    record = model.record(row)
    assert new_customer.company == record.value("company")
    assert new_customer.document_number == model.data(model.index(row, document_number))
    assert new_customer.address == model.data(model.index(row, address))


def test_deactivate_customer() -> None:
    db = _create_test_db()
    model = CustomersModel(db)
    model.add_customer(_add_customer())
    row = 0
    row_id = model.record(row).value("id")
    ok = model.set_active(row_id, True)
    assert ok
    assert model.record(row).value("active") == 1
    deactivate = model.set_active(row_id, active=False)
    assert deactivate
    assert model.record(row).value("active") == 0
