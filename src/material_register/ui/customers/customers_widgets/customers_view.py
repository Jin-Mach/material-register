from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTableView

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
        self._setup_ui(model)

    def _setup_ui(self, model: "CustomersModel") -> None:
        if not HeadersTexts.set_headers_text(self, model):
            dialog = ErrorDialog()
            dialog.show_dialog("TEXTS_LOAD_FAILED", False)
        hidden_columns = {
            "id": True,
            "notes": True,
            "created_at": True,
            "company_normalized": True,
            "first_name_normalized": True,
            "last_name_normalized": True,
            "address_normalized": True,
        }
        for index in range(model.columnCount()):
            name = model.record().fieldName(index)
            if name in hidden_columns:
                self.setColumnHidden(index, hidden_columns[name])