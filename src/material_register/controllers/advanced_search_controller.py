from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog

from material_register.ui.dialogs.advanced_search_dialog import AdvancedSearchDialog

if TYPE_CHECKING:
    from material_register.ui.search.search_widget import SearchWidget


class AdvancedSearchController(QObject):
    def __init__(self, search_widget: "SearchWidget") -> None:
        super().__init__(search_widget)
        self.search_widget = search_widget

    def start_advanced_filter(self) -> None:
        dialog = AdvancedSearchDialog(self.search_widget)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            print("OK")
