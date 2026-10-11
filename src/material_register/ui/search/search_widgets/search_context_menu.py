from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

if TYPE_CHECKING:
    from material_register.ui.search.search_widgets.search_transactions_view import (
        SearchTransactionsView,
    )


class SearchContextMenu(QMenu):
    def __init__(self, search_transactions_view: "SearchTransactionsView") -> None:
        super().__init__(search_transactions_view)
        self._create_ui()
        self._create_connection()
        self.transaction_index = None

    def _create_ui(self) -> None:
        self.show_transaction_document_action = QAction("Show transactions", self)
        self.show_transaction_document_action.setObjectName(
            "showTransactionDocumentAction"
        )
        self.addAction(self.show_transaction_document_action)

    def set_ui_texts(self, ui_texts: dict[str, str]) -> None:
        if ui_texts:
            for widget in self.findChildren(QAction):
                key = widget.objectName() + "Text"
                if key in ui_texts:
                    widget.setText(ui_texts[key])

    def _create_connection(self) -> None:
        pass

    def set_customer_index(self, index: QModelIndex) -> None:
        self.transaction_index = index

    def _show_document(self) -> None:
        if self.transaction_index is None:
            return
