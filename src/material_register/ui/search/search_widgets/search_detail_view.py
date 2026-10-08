from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHeaderView, QTableView

if TYPE_CHECKING:
    from material_register.ui.search.search_widgets.search_detail_widget import (
        SearchDetailWidget,
    )


class SearchDetailView(QTableView):
    def __init__(self, search_detail_widget: "SearchDetailWidget"):
        super().__init__(search_detail_widget)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.verticalHeader().hide()
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.NoSelection)
        self.setSortingEnabled(True)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)
