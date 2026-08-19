from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStackedWidget

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class SettingsStackedWidget(QStackedWidget):
    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        super().__init__(settings_dialog)