from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog

from material_register.services.db_cache import DbCache
from material_register.ui.dialogs.material_filter_dialog import MaterialFilterDialog

if TYPE_CHECKING:
    from material_register.db.models.search_models.material_filter_model import (
        MaterialFilterModel,
    )
    from material_register.ui.dialogs.advanced_search_dialog import AdvancedSearchDialog


class MaterialFilterController(QObject):
    def __init__(self, advanced_search_dialog: "AdvancedSearchDialog") -> None:
        super().__init__(advanced_search_dialog)
        self.advanced_search_dialog = advanced_search_dialog
        self._material_filter_model = None

    def set_material_filter_model(
        self, material_filter_model: "MaterialFilterModel"
    ) -> None:
        if self._material_filter_model is None:
            self._material_filter_model = material_filter_model

    def add_filter(self) -> None:
        dialog = MaterialFilterDialog(
            DbCache.categories, DbCache.commodities, self.advanced_search_dialog
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            text, filters = dialog.get_filters_data()
            print("text: ", text)
            print("filters:", filters)
