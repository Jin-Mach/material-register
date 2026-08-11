from PySide6.QtCore import QModelIndex, QSortFilterProxyModel, Qt

from material_register.utils.normalizer import normalize_text


class InventoryProxyFilter(QSortFilterProxyModel):
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
            value = normalize_text(model.data(index, Qt.ItemDataRole.DisplayRole))
            if text in value:
                return True
        return False
