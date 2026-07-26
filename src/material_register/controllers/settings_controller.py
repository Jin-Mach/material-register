from typing import TYPE_CHECKING

from material_register.providers.settings_provider import SettingsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog

if TYPE_CHECKING:
    from material_register.ui.settings.settings_widgets.export_setings import ExportSettings


class SettingsController:
    def __init__(self, export_settings: "ExportSettings") -> None:
        self.export_settings = export_settings
        self.settings = SettingsProvider.SETTINGS.get("export", {})

    def update_settings(self) -> None:
        user_settings = self.settings.get("user", {})
        new_data = self.export_settings.get_export_settings_data()
        if not user_settings or not new_data:
            SettingsController._handle_settings_error("Update settings failed",
                                                      f"{self.__class__.__name__}.update_settings")
            return
        for key, value in new_data.items():
            if key in user_settings:
                user_settings[key] = value
        if not SettingsProvider.save_settings():
            SettingsController._handle_settings_error("Update settings failed",
                                                      f"{self.__class__.__name__}.update_settings")
            return
        self._reload_settings()

    def _reload_settings(self) -> None:
        stacked_widget = self.export_settings.settings_widget.stacked_widget
        export_widget = stacked_widget.export_widget
        if hasattr(export_widget, "apply_settings"):
            export_widget.apply_settings()

    @staticmethod
    def _handle_settings_error(error: str, method: str) -> None:
        if not error:
            error = f"Settings failed: {method}"
        ErrorHandler.handle_error(error, "app", "warning")
        dialog = ErrorDialog()
        dialog.show_dialog("SETTINGS_FAILED", False)