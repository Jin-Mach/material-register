from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHeaderView, QSizePolicy, QTableView

if TYPE_CHECKING:
    from material_register.ui.search.search_tab_widget import SearchTabWidget


class SearchMaterialView(QTableView):
    def __init__(self, search_tab_widget: "SearchTabWidget") -> None:
        super().__init__(search_tab_widget)
        self.setObjectName("searchMaterialView")
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._setup_ui()

    def _setup_ui(self) -> None:
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setVerticalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QTableView.ScrollMode.ScrollPerPixel)
        self.verticalHeader().hide()
        self.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSortingEnabled(True)
        self.setCornerButtonEnabled(False)
        self.setAlternatingRowColors(True)
