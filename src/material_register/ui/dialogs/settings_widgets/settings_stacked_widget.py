from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStackedWidget

from material_register.ui.settings.settings_branch_widget import SettingsBranchWidget
from material_register.ui.settings.settings_documents_widget import (
    SettingsDocumentsWidget,
)
from material_register.ui.settings.settings_export_widget import SettingsExportWidget
from material_register.ui.settings.settings_tools_widget import SettingsToolsWidget

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class SettingsStackedWidget(QStackedWidget):
    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        super().__init__(settings_dialog)
        self.settings_dialog = settings_dialog
        self.settings_branch_widget = SettingsBranchWidget(self.settings_dialog)
        self.settings_export_widget = SettingsExportWidget(self.settings_dialog)
        self.settings_documents_widget = SettingsDocumentsWidget(self.settings_dialog)
        self.settings_tools_widget = SettingsToolsWidget(self.settings_dialog)
        self._init_setup()

    def _init_setup(self) -> None:
        widgets = [
            self.settings_branch_widget,
            self.settings_export_widget,
            self.settings_documents_widget,
            self.settings_tools_widget,
        ]
        for widget in widgets:
            self.addWidget(widget)
