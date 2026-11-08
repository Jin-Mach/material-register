from PySide6.QtGui import QStandardItem, QStandardItemModel, Qt

from material_register.domain.adavanced_search_dataclass import MaterialSearchDataclass


class MaterialFilterModel(QStandardItemModel):
    def add_filter(self, text: str, material_filter: MaterialSearchDataclass) -> None:
        item = MaterialFilterModel._create_filter_item(text, material_filter)
        self.appendRow(item)

    def update_filter(
        self, row: int, text: str, material_filter: MaterialSearchDataclass
    ) -> None:
        item = self.item(row)
        item.setText(text)
        item.setData(material_filter, Qt.ItemDataRole.UserRole)

    def remove_filter(self, row: int) -> None:
        self.removeRow(row)

    def get_filter_data(self, row: int) -> MaterialSearchDataclass:
        item = self.item(row)
        return item.data(Qt.ItemDataRole.UserRole)

    @staticmethod
    def _create_filter_item(
        filter_text: str, material_filter: MaterialSearchDataclass
    ) -> QStandardItem:
        item = QStandardItem()
        item.setText(filter_text)
        item.setData(material_filter, Qt.ItemDataRole.UserRole)
        item.setEditable(False)
        return item
