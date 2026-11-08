from typing import TYPE_CHECKING

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QDialog, QWidget

from material_register.services.db_cache import DbCache
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import LOG_LEVEL_WARNING, LOGGER_DB
from material_register.ui.dialogs.error_dialog import ErrorDialog
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
            if not text:
                return
            if self._material_filter_model is None:
                MaterialFilterController._handle_material_filter_error(
                    "MaterialFilterModel is None",
                    f"{self.__class__.__name__}._add_filter",
                    self.advanced_search_dialog,
                )
                return
            self._material_filter_model.add_filter(text, filters)

    def update_filter(self) -> None:
        index = self.advanced_search_dialog.material_search_widget.filters_list_view.currentIndex()
        if not index.isValid():
            return
        if self._material_filter_model is None:
            MaterialFilterController._handle_material_filter_error(
                "MaterialFilterModel is None",
                f"{self.__class__.__name__}._update_filter",
                self.advanced_search_dialog,
            )
            return
        filter_data = self._material_filter_model.get_filter_data(index.row())
        dialog = MaterialFilterDialog(
            DbCache.categories, DbCache.commodities, self.advanced_search_dialog
        )
        dialog.update_filter(filter_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            text, filters = dialog.get_filters_data()
            self._material_filter_model.update_filter(index.row(), text, filters)

    def delete_filter(self) -> None:
        index = self.advanced_search_dialog.material_search_widget.filters_list_view.currentIndex()
        if index.isValid() and self._material_filter_model is not None:
            self._material_filter_model.remove_filter(index.row())

    @staticmethod
    def _handle_material_filter_error(
        error: str,
        method: str,
        parent: QWidget,
        error_key: str = "UNKNOWN_ERROR",
    ) -> None:
        if not error:
            error = f"Unknown search error: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", LOGGER_DB, LOG_LEVEL_WARNING)
        ErrorDialog(parent).show_dialog(error_key, True)
