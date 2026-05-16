from typing import TYPE_CHECKING

from material_register.init.db_init import DbInit
from material_register.ui.dialogs.category_dialog import CategoryDialog

if TYPE_CHECKING:
    from material_register.ui.catalog.catalog_widget import CatalogWidget


class CatalogController:
    def __init__(self, catalog_widget: "CatalogWidget") -> None:
        self.catalog_widget = catalog_widget
        self.db_connection = DbInit.db_connection

    def add_category(self) -> None:
        dialog = CategoryDialog(self.catalog_widget)
        dialog.exec()