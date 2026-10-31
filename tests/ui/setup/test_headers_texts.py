import uuid
from collections.abc import Generator

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel
from PySide6.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel
from PySide6.QtWidgets import QTableView

from material_register.db.models.inventory_models.inventory_proxy_model import (
    InventoryProxyModel,
)
from material_register.db.models.search_models.search_material_model import (
    SearchMaterialModel,
)
from material_register.db.models.search_models.search_transactions_model import (
    SearchTransactionsModel,
)
from material_register.db.models.transactions_models.transactions_load_model_in import (
    TransactionsLoadModelIn,
)
from material_register.db.models.transactions_models.transactions_load_model_out import (
    TransactionsLoadModelOut,
)
from material_register.ui.setup.headers_texts import HeadersTexts


@pytest.fixture(autouse=True)
def reset_headers() -> Generator[None]:
    HeadersTexts.HEADERS_TEXTS = {}
    yield
    HeadersTexts.HEADERS_TEXTS = {}


@pytest.fixture
def sql_model(qtbot) -> QSqlTableModel:
    connection_name = f"test_ui_headers_texts_{uuid.uuid4().hex}"
    db = QSqlDatabase.addDatabase("QSQLITE", connection_name)
    db.setDatabaseName(":memory:")
    db.open()
    query = QSqlQuery(db)
    query.exec("CREATE TABLE test (id INTEGER, name TEXT)")
    query.exec("INSERT INTO test (id, name) VALUES (1, 'A')")
    model = QSqlTableModel(None, db)
    model.setTable("test")
    model.select()
    return model


def test_set_headers_text_success(qtbot, sql_model: QSqlTableModel) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    HeadersTexts.setup_init({"QTableView": {"id": "ID Column", "name": "Name Column"}})
    result = HeadersTexts.set_headers_text(view, sql_model)
    assert result is True
    assert sql_model.headerData(0, Qt.Orientation.Horizontal) == "ID Column"
    assert sql_model.headerData(1, Qt.Orientation.Horizontal) == "Name Column"


def test_set_headers_text_partial_mapping(qtbot, sql_model: QSqlTableModel) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    HeadersTexts.setup_init({"QTableView": {"name": "Only Name"}})
    result = HeadersTexts.set_headers_text(view, sql_model)
    assert result is True
    assert sql_model.headerData(1, Qt.Orientation.Horizontal) == "Only Name"


def test_set_headers_text_no_config(qtbot, sql_model: QSqlTableModel) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    HeadersTexts.setup_init({})
    result = HeadersTexts.set_headers_text(view, sql_model)
    assert result is False


def test_set_headers_text_invalid_key(qtbot, sql_model: QSqlTableModel) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    HeadersTexts.setup_init({"QTableView": {"wrong_column": "X"}})
    result = HeadersTexts.set_headers_text(view, sql_model)
    assert result is True


def test_set_headers_text_standard_item_model(qtbot) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    model = QStandardItemModel()
    model.setColumnCount(3)
    HeadersTexts.setup_init(
        {
            "QTableView": {
                "column1": "First Column",
                "column2": "Second Column",
                "column3": "Third Column",
            }
        }
    )
    result = HeadersTexts.set_headers_text(view, model)
    assert result is True
    assert model.headerData(0, Qt.Orientation.Horizontal) == "First Column"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Second Column"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Third Column"


@pytest.mark.parametrize(
    "model_class", [TransactionsLoadModelIn, TransactionsLoadModelOut]
)
def test_set_transactions_headers_text_success(
    qtbot, sql_model: QSqlTableModel, model_class
) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    model = model_class(sql_model.database())
    HeadersTexts.setup_init(
        {
            "QTableView": {
                "headers_texts": {
                    "0": "Date",
                    "1": "Customer",
                    "2": "Document",
                    "3": "Address",
                    "4": "Total",
                }
            }
        }
    )
    result = HeadersTexts.set_transactions_headers_text(view, model)
    assert result is True
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Date"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Customer"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Document"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Address"
    assert model.headerData(4, Qt.Orientation.Horizontal) == "Total"


@pytest.mark.parametrize(
    "model_class", [TransactionsLoadModelIn, TransactionsLoadModelOut]
)
def test_set_transactions_headers_text_no_config(
    qtbot, sql_model: QSqlTableModel, model_class
) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    model = model_class(sql_model.database())
    HeadersTexts.setup_init({})
    result = HeadersTexts.set_transactions_headers_text(view, model)
    assert result is False


def test_set_inventory_headers_text_success(qtbot) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    source_model = QStandardItemModel()
    source_model.setColumnCount(5)
    model = InventoryProxyModel()
    model.setSourceModel(source_model)
    HeadersTexts.setup_init(
        {
            "QTableView": {
                "0": "Category",
                "1": "Item",
                "2": "Unit",
                "3": "Stock quantity",
                "4": "Status",
            }
        }
    )
    result = HeadersTexts.set_inventory_headers_text(view, model)
    assert result is True
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Category"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Item"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Unit"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Stock quantity"
    assert model.headerData(4, Qt.Orientation.Horizontal) == "Status"


def test_set_inventory_headers_text_no_config(qtbot) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    source_model = QStandardItemModel()
    source_model.setColumnCount(5)
    model = InventoryProxyModel()
    model.setSourceModel(source_model)
    HeadersTexts.setup_init({})
    result = HeadersTexts.set_inventory_headers_text(view, model)
    assert result is False


def test_set_search_headers_text_success(qtbot) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    model = SearchTransactionsModel()
    HeadersTexts.setup_init(
        {
            "QTableView": {
                "headers_texts": {
                    "0": "ID",
                    "1": "Type",
                    "2": "Date",
                    "3": "Customer",
                    "4": "Document",
                    "5": "Address",
                    "6": "Total",
                }
            }
        }
    )
    result = HeadersTexts.set_search_headers_text(view, model)
    assert result is True
    assert model.headerData(0, Qt.Orientation.Horizontal) == "ID"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Type"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Date"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Customer"
    assert model.headerData(4, Qt.Orientation.Horizontal) == "Document"
    assert model.headerData(5, Qt.Orientation.Horizontal) == "Address"
    assert model.headerData(6, Qt.Orientation.Horizontal) == "Total"


def test_set_search_headers_text_no_config(qtbot) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    model = SearchTransactionsModel()
    HeadersTexts.setup_init({})
    result = HeadersTexts.set_search_headers_text(view, model)
    assert result is False


def test_set_material_headers_text_success(qtbot) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    model = SearchMaterialModel()
    HeadersTexts.setup_init(
        {
            "QTableView": {
                "headers_texts": {
                    "0": "Category",
                    "1": "Item",
                    "2": "Unit",
                    "3": "Net Movement",
                }
            }
        }
    )
    result = HeadersTexts.set_material_headers_text(view, model)
    assert result is True
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Category"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Item"
    assert model.headerData(2, Qt.Orientation.Horizontal) == "Unit"
    assert model.headerData(3, Qt.Orientation.Horizontal) == "Net Movement"


def test_set_material_headers_text_no_config(qtbot) -> None:
    view = QTableView()
    qtbot.addWidget(view)
    model = SearchMaterialModel()
    HeadersTexts.setup_init({})
    result = HeadersTexts.set_material_headers_text(view, model)
    assert result is False
