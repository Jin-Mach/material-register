from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

from material_register.core.app_context import AppContext
from material_register.db.queries.category_queries import CategoryQueries
from material_register.db.queries.commodities_queries import CommoditiesQueries
from material_register.domain.commodities_dataclass import Commodity
from material_register.init.db_init import DbInit
from material_register.providers.texts_provider import TextsProvider
from material_register.services.db_cache import DbCache
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
            if category_data is None:
                error_dialog = ErrorDialog()
                error_dialog.show_dialog("UNKNOWN_ERROR", False)
                return
            ok, error, category_id = CategoryQueries.create_category(self.db_connection, category_data.name, category_data.notes)
            if not ok:
                CatalogController._handle_db_error(error, f"{self.__class__.__name__}.add_category")
                return
            category_data.id = category_id
            CatalogController._refresh_cache()
            self.reload_catalog_tree()
            self.catalog_widget.details_widget.refresh_category_data(category_data)
            item = self.catalog_widget.tree_widget.find_item_by_id(category_id)
            if item:
                self.catalog_widget.tree_widget.setCurrentItem(item)
            CatalogController._notification_handler(self.notification_texts, "ADD_CATEGORY", "Category added")

    def add_commodity(self) -> None:
        category, _ = self.catalog_widget.tree_widget.get_selected_data()
        if category is None:
            return
        dialog = CommodityDialog(self.catalog_widget, category.id, category.name)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            commodity_data = dialog.get_commodity_data()
            if not commodity_data:
                error_dialog = ErrorDialog()
                error_dialog.show_dialog("UNKNOWN_ERROR", False)
                return
            ok, error = CommoditiesQueries.create_commodity(self.db_connection, commodity_data.name, category.id,
                                                            commodity_data.unit, commodity_data.default_price,
                                                            commodity_data.notes, commodity_data.active)
            if not ok:
                CatalogController._handle_db_error(error, f"{self.__class__.__name__}.add_commodity")
                return
            parent_item, item = self.catalog_widget.tree_widget.create_commodity_item(commodity_data)
            if parent_item is None or item is None:
                error_dialog = ErrorDialog()
                error_dialog.show_dialog("UNKNOWN_ERROR", False)
                return
            self.catalog_widget.tree_widget.setCurrentItem(item)
            parent_item.setExpanded(True)
            CatalogController._refresh_cache()
            self.setup_details_widget()
            CatalogController._notification_handler(self.notification_texts, "ADD_COMMODITY", "Commodity added")

    def update_category(self) -> None:
        category, _ = self.catalog_widget.tree_widget.get_selected_data()
        if not category:
            return
        dialog = CategoryDialog(self.catalog_widget, mode="UPDATE", category_data=category)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            category_data = dialog.get_category_data()
            if category_data is None:
                error_dialog = ErrorDialog()
                error_dialog.show_dialog("UNKNOWN_ERROR", False)
                return
            ok, error = CategoryQueries.update_category(self.db_connection, category.id, category_data.name,
                                                        category_data.notes)
            if not ok:
                CatalogController._handle_db_error(error, f"{self.__class__.__name__}.update_category")
                return
            CatalogController._refresh_cache()
            self.reload_catalog_tree()
            self.catalog_widget.details_widget.refresh_category_data(category_data)
            item = self.catalog_widget.tree_widget.find_item_by_id(category.id)
            if item is not None:
                self.catalog_widget.tree_widget.setCurrentItem(item)
                item.setExpanded(True)
            CatalogController._notification_handler(self.notification_texts, "UPDATE_CATEGORY", "Category updated")

    def update_commodity(self, commodity: Commodity) -> None:
        category, _ = self.catalog_widget.tree_widget.get_selected_data()
        if category is None:
            return
        dialog = CommodityDialog(self.catalog_widget, commodity.category_id, category.name, mode="UPDATE",
                                 commodity_data=commodity)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            commodity_data = dialog.get_commodity_data()
            if not commodity_data:
                error_dialog = ErrorDialog()
                error_dialog.show_dialog("UNKNOWN_ERROR", False)
                return
            ok, error = CommoditiesQueries.update_commodity(self.db_connection, commodity_data.id, commodity_data.name,
                                                            commodity_data.category_id, commodity_data.unit,
                                                            commodity_data.default_price, commodity_data.notes,
                                                            commodity_data.active)
            if not ok:
                CatalogController._handle_db_error(error, f"{self.__class__.__name__}.update_commodity")
                return
            CatalogController._refresh_cache()
            self.reload_catalog_tree()
            self.setup_details_widget()
            item = self.catalog_widget.tree_widget.find_item_by_id(category.id)
            if item is not None:
                self.catalog_widget.tree_widget.setCurrentItem(item)
                item.setExpanded(True)
            CatalogController._notification_handler(self.notification_texts, "UPDATE_COMMODITY", "Item updated")

    def reload_catalog_tree(self) -> None:
        self.catalog_widget.tree_widget.reload_tree(DbCache.categories, DbCache.commodities)

    def category_exists(self, name: str, ignored_id: int | None = None) -> bool:
        return CategoryQueries.category_exists(self.db_connection, name, ignored_id)

    def commodity_exists(self, name: str, ignored_id: int | None = None) -> bool:
        return CommoditiesQueries.commodity_exists(self.db_connection, name, ignored_id)

    def setup_details_widget(self) -> None:
        category, _ = self.catalog_widget.tree_widget.get_selected_data()
        if category is None:
            self.catalog_widget.details_widget.stacked_widget.setCurrentIndex(0)
            return
        commodities = CatalogController._get_commodities_for_category(category.id)
        self.catalog_widget.details_widget.stacked_widget.setCurrentIndex(1)
        self.catalog_widget.details_widget.category_with_commodities_widget.setup_ui(category, commodities)

    @staticmethod
    def _refresh_cache() -> None:
        DbCache.refresh_catalog_data()

    @staticmethod
    def _get_commodities_for_category(category_id: int) -> list[Commodity]:
        commodities = []
        for commodity in DbCache.commodities:
            if commodity.category_id == category_id:
                commodities.append(commodity)
        return sorted(commodities, key=lambda commodity_item: commodity_item.name.lower())

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