from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from material_register.providers.settings_provider import SettingsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.setup.ui_settings import UiSettings

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog
    from material_register.ui.settings.settings_branch_widget import (
        SettingsBranchWidget,
    )


class BranchSettingsController:
    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        self.settings_dialog = settings_dialog
        self.settings = UiSettings.SETTINGS.get("branch", {})

    def update_branch_settings(
        self, settings_branch_widget: "SettingsBranchWidget"
    ) -> None:
        new_data = settings_branch_widget.branch_settings_data()
        if not new_data:
            self._handle_settings_error(
                "Update settings failed",
                f"{self.__class__.__name__}.update_branch_settings",
                self.settings_dialog,
            )
            return
        for key, value in new_data.items():
            if key in self.settings:
                self.settings[key] = value
        if not SettingsProvider.save_settings():
            self._handle_settings_error(
                "Update settings failed",
                f"{self.__class__.__name__}.update_branch_settings",
                self.settings_dialog,
            )
            return
        self.settings_dialog.set_info_text("SETTINGS_SAVED")

    @staticmethod
    def _handle_settings_error(error: str, method: str, parent: QWidget) -> None:
        if not error:
            error = f"Settings failed: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", "settings", "warning")
        ErrorDialog(parent).show_dialog("SETTINGS_FAILED", False)
