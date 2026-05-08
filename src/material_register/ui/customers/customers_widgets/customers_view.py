from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTableView

if TYPE_CHECKING:
    from material_register.ui.widgets.stacked_widget import StackedWidget


class CustomersView(QTableView):
    def __init__(self, stacked_widget: "StackedWidget") -> None:
        super().__init__(stacked_widget)