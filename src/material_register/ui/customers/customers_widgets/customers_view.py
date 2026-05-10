from typing import TYPE_CHECKING

from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QTableView, QHeaderView

from material_register.services.error_handler import ErrorHandler
from material_register.ui.customers.customers_widgets.customers_context_menu import CustomersContextMenu
from material_register.ui.setup.headers_texts import HeadersTexts
from material_register.db.models.customers_model import CustomersModel
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.customers.customers_widget import CustomersWidget


class CustomersView(QTableView):
    HIDDEN_COLUMNS = ("id", "first_name", "last_name", "notes", "created_at", "company_normalized",
                      "first_name_normalized", "last_name_normalized", "address_normalized")
    HORIZONTAL_PADDING = 50

    def __init__(self, customers_widget: "CustomersWidget") -> None:
        super().__init__(customers_widget)
        self.customers_widget = customers_widget

    def setModel(self, model: CustomersModel) -> None:
        super().setModel(model)

    def setup_ui(self) -> None:
        model = self.model()
        error = "TEXTS_LOAD_FAILED"
        if not isinstance(model, CustomersModel):
            return
        if not HeadersTexts.set_headers_text(self, model):
            ErrorHandler.handle_error(f"Headers text load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = error
        self.menu_texts = UiTexts.UI_TEXTS.get(self.__class__.__name__, {})
        if not self.menu_texts:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = error
            self.menu_texts = UiTexts.DEFAULT_TEXTS.get(self.__class__.__name__, {})
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
        for col in range(model.columnCount()):
            if col == address_column:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
        self.update_headers(model)

    def update_headers(self, model: CustomersModel) -> None:
        address_column = model.fieldIndex("address")
        active_column = model.fieldIndex("active")
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
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def open_context_menu(self, position: QPoint) -> None:
        index = self.indexAt(position)
        if not index.isValid():
            return
        menu = CustomersContextMenu(self, self.customers_widget.customers_controller)
        menu.set_customer_index(index)
        if not self.menu_texts:
            ErrorHandler.handle_error(f"Texts load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = True
        menu.set_ui_texts(self.menu_texts)
        menu.exec_(self.mapToGlobal(position))