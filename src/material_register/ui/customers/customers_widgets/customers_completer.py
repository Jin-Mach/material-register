from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QCompleter


class CustomersCompleter(QCompleter):
    def __init__(self) -> None:
        super().__init__()
        self.popup().setObjectName("customerCompleterPopup")
        self.setCompletionRole(Qt.ItemDataRole.UserRole + 11)
        self.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setFilterMode(Qt.MatchFlag.MatchContains)

    def pathFromIndex(self, index: QModelIndex) -> str:
        return index.data(Qt.ItemDataRole.UserRole + 10)
