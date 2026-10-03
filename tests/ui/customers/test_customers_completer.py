from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from material_register.ui.customers.customers_widgets.customers_completer import (
    CustomersCompleter,
)


def test_customers_completer_returns_original_name() -> None:
    model = QStandardItemModel()
    item = QStandardItem()
    item.setData("André Miller", Qt.ItemDataRole.UserRole + 10)
    item.setData("andre miller", Qt.ItemDataRole.UserRole + 11)
    model.appendRow(item)
    completer = CustomersCompleter()
    completer.setModel(model)
    index = model.index(0, 0)
    assert completer.pathFromIndex(index) == "André Miller"
