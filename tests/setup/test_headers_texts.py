import pytest

from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide6.QtWidgets import QTableView
from material_register.ui.setup.headers_texts import HeadersTexts


@pytest.fixture(autouse=True)
def reset_headers():
    HeadersTexts.HEADERS_TEXTS = {}
    yield
    HeadersTexts.HEADERS_TEXTS = {}

@pytest.fixture
def sql_model(qtbot):
    db = QSqlDatabase.addDatabase("QSQLITE", "test_conn")
    db.setDatabaseName(":memory:")
    db.open()
    query = QSqlQuery(db)
    query.exec("CREATE TABLE test (id INTEGER, name TEXT)")
    query.exec("INSERT INTO test (id, name) VALUES (1, 'A')")
    model = QSqlTableModel(None, db)
    model.setTable("test")
    model.select()
    return model

def test_set_headers_text_success(qtbot, sql_model):
    view = QTableView()
    qtbot.addWidget(view)
    HeadersTexts.setup_init({
        "QTableView": {
            "id": "ID Column",
            "name": "Name Column"
        }
    })
    result = HeadersTexts.set_headers_text(view, sql_model)
    assert result is True
    assert sql_model.headerData(0, Qt.Orientation.Horizontal) == "ID Column"
    assert sql_model.headerData(1, Qt.Orientation.Horizontal) == "Name Column"

def test_set_headers_text_partial_mapping(qtbot, sql_model):
    view = QTableView()
    qtbot.addWidget(view)
    HeadersTexts.setup_init({
        "QTableView": {
            "name": "Only Name"
        }
    })
    result = HeadersTexts.set_headers_text(view, sql_model)
    assert result is True
    assert sql_model.headerData(1, Qt.Orientation.Horizontal) == "Only Name"

def test_set_headers_text_no_config(qtbot, sql_model):
    view = QTableView()
    qtbot.addWidget(view)
    HeadersTexts.setup_init({})
    result = HeadersTexts.set_headers_text(view, sql_model)
    assert result is False

def test_set_headers_text_invalid_key(qtbot, sql_model):
    view = QTableView()
    qtbot.addWidget(view)
    HeadersTexts.setup_init({
        "QTableView": {
            "wrong_column": "X"
        }
    })
    result = HeadersTexts.set_headers_text(view, sql_model)
    assert result is True