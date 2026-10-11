from PySide6.QtCore import QCollator, QModelIndex, QSortFilterProxyModel, Qt

from material_register.db.config.model_constants import LOAD_MODEL_COLUMNS


class TransactionsProxyModel(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self._collator = QCollator()
        self._collator.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
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

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        column = LOAD_MODEL_COLUMNS[left.column()]
        if column == "transaction_created_at" or column == "total":
            left_value = self.sourceModel().data(left, Qt.ItemDataRole.UserRole)
            right_value = self.sourceModel().data(right, Qt.ItemDataRole.UserRole)
            return left_value < right_value
        else:
            left_value = self.sourceModel().data(left, Qt.ItemDataRole.DisplayRole)
            right_value = self.sourceModel().data(right, Qt.ItemDataRole.DisplayRole)
            return self._collator.compare(str(left_value), str(right_value)) < 0
