from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem

from material_register.ui.setup.ui_icons import UiIcons

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.database_backup_widget import (
        DatabaseBackupWidget,
    )


class DatabaseBackupTreeWidget(QTreeWidget):
    def __init__(self, database_backup_widget: "DatabaseBackupWidget") -> None:
        super().__init__(database_backup_widget)
        self.setHeaderHidden(True)
        self.setSortingEnabled(True)
        self.sortItems(0, Qt.SortOrder.DescendingOrder)
        self._create_connection()

    def _create_connection(self) -> None:
        self.itemExpanded.connect(
            lambda item: UiIcons.set_tree_widget_icon(item, expanded=True)
        )
        self.itemCollapsed.connect(lambda item: UiIcons.set_tree_widget_icon(item))

    def load_tree_widget(self, backup_map: dict[str, list[Path]]) -> None:
        self.clear()
        for year, backups in backup_map.items():
            year_item = QTreeWidgetItem([year])
            self.addTopLevelItem(year_item)
            UiIcons.set_tree_widget_icon(year_item)
            for backup in backups:
                name = DatabaseBackupTreeWidget._get_backup_name(backup)
                backup_item = QTreeWidgetItem([name])
                backup_item.setData(0, Qt.ItemDataRole.UserRole, backup)
                year_item.addChild(backup_item)

    def get_selected_data(self) -> Path | None:
        item = self.currentItem()
        if item is None:
            return None
        if item.parent() is None:
            return None
        return item.data(0, Qt.ItemDataRole.UserRole)

    @staticmethod
    def _get_backup_name(backup_path: Path) -> str:
        backup_name = backup_path.stem
        if backup_name.startswith("backup_"):
            backup_name = backup_name.removeprefix("backup_")
        return backup_name
