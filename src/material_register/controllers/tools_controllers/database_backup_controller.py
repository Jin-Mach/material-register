from datetime import datetime, UTC
from typing import TYPE_CHECKING

from material_register.db.config.db_constants import DATABASE_NAME
from material_register.providers.paths_provider import PathsProvider
from material_register.ui.helpers.formating_utils import format_datetime_to_locale

if TYPE_CHECKING:
    from material_register.ui.tools.right_toolbar_widgets.database_backup_widget import DatabaseBackupWidget


class DatabaseBackupController:
    def __init__(self, database_backup_widget: "DatabaseBackupWidget") -> None:
        self.database_backup_widget = database_backup_widget
        self.database_path = (PathsProvider.database / DATABASE_NAME).with_suffix(".db")

    def setup_database_info_group(self) -> tuple[str, str, str]:
        database_stat = self.database_path.stat()
        name = self.database_path.name
        size = int(database_stat.st_size)
        if size < 1024 * 1024:
            size_text = f"{size / 1024:.1f} KB"
        else:
            size_text = f"{size / (1024 ** 2):.1f} MB"
        last_modify = format_datetime_to_locale(
            datetime.fromtimestamp(database_stat.st_mtime, UTC).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
        return name, size_text, last_modify
