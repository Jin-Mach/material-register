from PySide6.QtCore import QSortFilterProxyModel, Qt, QModelIndex


class TransactionsProxyFilter(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self._text = ""

    def set_filtered_text(self, text: str) -> None:
        self._text = text
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        model = self.sourceModel()
        index = model.index(source_row, 0, source_parent)
        value = model.data(index, Qt.ItemDataRole.UserRole)
        if not self._text:
            return True
        if value is None:
            return False
        if self._text in value:
            return True
        return False