from PySide6.QtCore import QModelIndex, QSortFilterProxyModel, Qt


class TransactionsProxyFilter(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self._text = ""

    def set_filtered_text(self, text: str) -> None:
        self._text = text
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self._text:
            return True
        text = self._text.lower()
        model = self.sourceModel()
        column_count = model.columnCount(source_parent)
        for column in range(column_count):
            index = model.index(source_row, column, source_parent)
            value = model.data(index, Qt.ItemDataRole.UserRole)
            if isinstance(value, str) and text in value:
                return True
        return False
