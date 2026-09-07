from typing import TYPE_CHECKING

from PySide6.QtWidgets import QTreeWidget

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.database_backup_widget import (
        DatabaseBackupWidget,
    )


class DatabaseBackupTreeWidget(QTreeWidget):
    def __init__(self, database_backup_widget: "DatabaseBackupWidget") -> None:
        super().__init__(database_backup_widget)
        self.setHeaderHidden(True)
