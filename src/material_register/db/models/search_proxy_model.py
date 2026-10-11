from PySide6.QtCore import QCollator, QLocale, QModelIndex, QSortFilterProxyModel, Qt

from material_register.db.config.model_constants import SEARCH_MODEL_COLUMNS


class SearchProxyModel(QSortFilterProxyModel):
    def __init__(self) -> None:
        super().__init__()
        self._collator = QCollator(QLocale())
        self._collator.setCaseSensitivity(Qt.CaseSensitivity.CaseSensitive)

    def lessThan(self, left: QModelIndex, right: QModelIndex) -> bool:
        column = SEARCH_MODEL_COLUMNS[left.column()]
        if column == "transaction_created_at" or column == "total":
            left_value = self.sourceModel().data(left, Qt.ItemDataRole.UserRole)
            right_value = self.sourceModel().data(right, Qt.ItemDataRole.UserRole)
            return left_value < right_value
        else:
            left_value = self.sourceModel().data(left, Qt.ItemDataRole.DisplayRole)
            right_value = self.sourceModel().data(right, Qt.ItemDataRole.DisplayRole)
            return self._collator.compare(str(left_value), str(right_value)) < 0
