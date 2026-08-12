from typing import TYPE_CHECKING

from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.inventory.inventory_widget import InventoryWidget


class InventoryActionsWidget(QWidget):
    def __init__(self, inventory_widget: "InventoryWidget") -> None:
        super().__init__(inventory_widget)
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QHBoxLayout:
        main_layout = QHBoxLayout()
        self.search_line_edit = QLineEdit()
        self.search_line_edit.setObjectName("searchLineEdit")
        self.search_line_edit.setMinimumWidth(600)
        main_layout.addStretch()
        main_layout.addWidget(self.search_line_edit)
        main_layout.addStretch()
        return main_layout

    def _setup_ui(self) -> None:
        widgets = [self.search_line_edit]
        self._setup_texts(widgets)

    def _setup_texts(self, widgets: list[QWidget]) -> None:
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)
