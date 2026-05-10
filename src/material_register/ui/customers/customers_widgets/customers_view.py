from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTableView, QHeaderView

from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.setup.headers_texts import HeadersTexts
from material_register.db.models.customers_model import CustomersModel

if TYPE_CHECKING:
    from material_register.ui.customers.customers_widget import CustomersWidget


class CustomersView(QTableView):
    HIDDEN_COLUMNS = ("id", "first_name", "last_name", "notes", "created_at", "company_normalized",
                      "first_name_normalized", "last_name_normalized", "address_normalized")
    HORIZONTAL_PADDING = 50

    def __init__(self, customers_widget: "CustomersWidget") -> None:
        super().__init__(customers_widget)

    def setModel(self, model: CustomersModel) -> None:
        super().setModel(model)

    def setup_ui(self) -> None:
        model = self.model()
        if not isinstance(model, CustomersModel):
            return
        if not HeadersTexts.set_headers_text(self, model):
            ErrorDialog().show_dialog("TEXTS_LOAD_FAILED", False)
        self._setup_columns(model)
        self._setup_headers(model)
        self._setup_behavior()

    def _setup_columns(self, model: CustomersModel) -> None:
        for name in self.HIDDEN_COLUMNS:
            index = model.fieldIndex(name)
            if index >= 0:
                self.setColumnHidden(index, True)

    def _setup_headers(self, model: CustomersModel) -> None:
        header = self.horizontalHeader()
        address_column = model.fieldIndex("address")
        active_column = model.fieldIndex("active")
        for col in range(model.columnCount()):
            if col == address_column:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
        self.resizeColumnsToContents()
        for col in range(model.columnCount()):
            if col in (address_column, active_column):
                continue
            self.setColumnWidth(col, self.columnWidth(col) + self.HORIZONTAL_PADDING)

    def _setup_behavior(self) -> None:
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectItems)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)