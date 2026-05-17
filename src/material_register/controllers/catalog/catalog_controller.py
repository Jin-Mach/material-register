from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QTreeWidgetItem

from material_register.core.app_context import AppContext
from material_register.db.queries.category_queries import CategoryQueries
from material_register.domain.category_dataclass import Category
from material_register.init.db_init import DbInit
from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.category_dialog import CategoryDialog
from material_register.ui.dialogs.commodity_dialog import CommodityDialog
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
            ok, error = CategoryQueries.create_category(self.db_connection, category_data.name, category_data.notes)
            if not ok:
                CatalogController._handle_db_error(error, f"{self.__class__.__name__}.add_category")
                return
            item = self.catalog_widget.tree_widget.create_category_item(category_data)
            self.catalog_widget.tree_widget.addTopLevelItem(item)
            self.catalog_widget.tree_widget.setCurrentItem(item)
            self.catalog_widget.details_widget.category_detail_widget.set_category_texts(category_data)
            self._notification_handler(self.notification_texts, "ADD_CATEGORY", "Category added")

    def add_commodity(self) -> None:
        category = self.catalog_widget.tree_widget.get_selected_category()
        if not category:
            return
        dialog = CommodityDialog(self.catalog_widget, category.id, category.name)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            commodity_data = dialog.get_commodity_data()
            print("commodity data:", commodity_data)

    def update_category(self) -> None:
        item = self.catalog_widget.tree_widget.currentItem()
        if not item:
            return
        category = item.data(0, Qt.ItemDataRole.UserRole)
        if not isinstance(category, Category):
            return
        if category.id is None or category.id <= 0:
            return
        if category is None:
            ErrorDialog().show_dialog("DATABASE_ERROR", False)
            return
        dialog = CategoryDialog(self.catalog_widget, mode="UPDATE", category_data=category)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            category_data = dialog.get_category_data()
            if category_data is None:
                ErrorDialog().show_dialog("UNKNOWN_ERROR", False)
                return
            ok, error = CategoryQueries.update_category(self.db_connection, category.id, category_data.name,
                                                        category_data.notes)
            if not ok:
                CatalogController._handle_db_error(error, f"{self.__class__.__name__}.update_category")
                return
            self.load_categories_to_tree()
            self.catalog_widget.details_widget.category_detail_widget.set_category_texts(category_data)
            CatalogController._notification_handler(self.notification_texts, "UPDATE_CATEGORY", "Category updated")

    def load_categories_to_tree(self) -> None:
        categories = CategoryQueries.get_categories(self.db_connection)
        tree = self.catalog_widget.tree_widget
        tree.clear()
        for category in categories:
            item = QTreeWidgetItem([category.name])
            item.setData(0, Qt.ItemDataRole.UserRole, category)
            tree.addTopLevelItem(item)

    def category_exists(self, name: str, ignored_id: int | None = None) -> bool:
        return CategoryQueries.category_exists(self.db_connection, name, ignored_id)

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