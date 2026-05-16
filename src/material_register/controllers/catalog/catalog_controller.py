from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QTreeWidgetItem

from material_register.core.app_context import AppContext
from material_register.db.queries.catalog_queries import CatalogQueries
from material_register.init.db_init import DbInit
from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.category_dialog import CategoryDialog
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.notification_dialog import NotificationDialog

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogController:
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        self.catalog_widget = catalog_widget
        self.db_connection = DbInit.db_connection
        self.notification_texts = TextsProvider.NOTIFICATION_TEXTS.get("CATALOG", None)

    def add_category(self) -> None:
        dialog = CategoryDialog(self.catalog_widget)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            category_data = dialog.get_category_data()
            if not category_data:
                dialog = ErrorDialog()
                dialog.show_dialog("UNKNOWN_ERROR", False)
                return
            name = category_data.get("name")
            notes = category_data.get("notes")
            ok, error = CatalogQueries.create_category(self.db_connection, name, notes)
            if not ok:
                CatalogController._handle_db_error(error, f"{self.__class__.__name__}.add_category")
                return
            self.load_categories_to_tree()

    def load_categories_to_tree(self) -> None:
        categories = CatalogQueries.get_categories(self.db_connection)
        tree = self.catalog_widget.tree_widget
        tree.clear()
        for cat in categories:
            item = QTreeWidgetItem([cat["name"]])
            item.setData(0, Qt.ItemDataRole.UserRole, cat["id"])
            tree.addTopLevelItem(item)

    def category_exists(self, name: str, ignored_id: int | None = None) -> bool:
        return CatalogQueries.category_exists(self.db_connection, name, ignored_id)

    @staticmethod
    def _handle_db_error(error: str, method: str) -> None:
        if not error:
            error = f"Unknown database error: {method}"
        ErrorHandler.handle_error(error, "db", "critical")
        ErrorDialog().show_dialog("DATABASE_ERROR", False)

    @staticmethod
    def _notification_handler(notification_texts: dict[str, str], key: str, default: str) -> None:
        if notification_texts is None:
            return
        notification = NotificationDialog(AppContext.MAIN_WINDOW, notification_texts.get(key, default))
        notification.show_notification()