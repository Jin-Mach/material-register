import pytest
from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.customers_queries import CustomersQueries


@pytest.fixture
def connection() -> QSqlDatabase:
    conn = QSqlDatabase.addDatabase('QSQLITE')
    conn.setDatabaseName(":memory:")
    conn.open()
    return conn

@pytest.fixture
def schema(connection) -> None:
    query = QSqlQuery(connection)
    ok = query.exec("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            first_name TEXT,
            last_name TEXT,
            document_number TEXT NOT NULL UNIQUE,
            address TEXT NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1,
            company_normalized TEXT,
            first_name_normalized TEXT,
            last_name_normalized TEXT,
            address_normalized TEXT
        )
    """)
    assert ok, query.lastError().text()

def test_get_customers(connection, schema):
    query = QSqlQuery(connection)
    query.exec("""
        INSERT INTO customers
        (company, first_name, last_name, document_number, address, active)
        VALUES ('A', 'Joe', 'Doe', '123', 'Earth', 1)
    """)
    data = CustomersQueries.get_customers(connection)
    assert len(data) == 1
    assert data[0].company == "A"
    assert data[0].first_name == "Joe"
    assert data[0].last_name == "Doe"
    assert data[0].document_number == "123"
    assert data[0].address == "Earth"
    assert data[0].active == 1