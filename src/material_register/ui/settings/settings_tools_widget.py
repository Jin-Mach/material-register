from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class SettingsToolsWidget(QWidget):
    def __init__(self, settings_dialog: "SettingsDialog"):
        super().__init__(settings_dialog)
        self.settings_dialog = settings_dialog
