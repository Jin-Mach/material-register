from typing import TYPE_CHECKING

from PySide6.QtSql import QSqlTableModel
from PySide6.QtWidgets import QTableView, QHeaderView

from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.setup.headers_texts import HeadersTexts

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget
    from material_register.db.models.customers_model import CustomersModel


class CustomersView(QTableView):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)

    def setModel(self, model: "CustomersModel") -> None:
        super().setModel(model)
        model.select()

    def setup_ui(self) -> None:
        model = self.model()
        if not isinstance(model, QSqlTableModel) or model is None:
            return
        if not HeadersTexts.set_headers_text(self, model):
            dialog = ErrorDialog()
            dialog.show_dialog("TEXTS_LOAD_FAILED", False)
        hidden_columns = ("id", "first_name", "last_name", "notes", "created_at", "company_normalized",
                          "first_name_normalized", "last_name_normalized", "address_normalized")
        for name in hidden_columns:
            index = model.fieldIndex(name)
            if index >= 0:
                self.setColumnHidden(index, True)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        address_column = model.fieldIndex("address")
        if address_column >= 0:
            header.setSectionResizeMode(address_column, QHeaderView.ResizeMode.Stretch)
        self.resizeColumnsToContents()