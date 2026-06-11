import pytest

from PySide6.QtSql import QSqlDatabase, QSqlQuery

from material_register.db.queries.transactions_queries import TransactionsQueries


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
        CREATE TABLE transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,
            customer_id INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            payment_type TEXT,
            notes TEXT
        )
    """)

def test_insert_into_transactions(connection, schema) -> None:
    ok, error, transaction_id = TransactionsQueries.insert_into_transactions(connection, "IN",
                                                                             1, "CASH",
                                                                             "notes")
    assert ok == True
    assert error == ""
    assert isinstance(transaction_id, int)
    query = QSqlQuery(connection)
    query.exec("SELECT type, customer_id, payment_type, notes FROM transactions")
    assert query.next()
    assert query.value(0) == "IN"
    assert query.value(1) == 1
    assert query.value(2) == "CASH"
    assert query.value(3) == "notes"