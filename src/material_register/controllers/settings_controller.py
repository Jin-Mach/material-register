from typing import TYPE_CHECKING

from material_register.core.app_context import AppContext
from material_register.providers.settings_provider import SettingsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes

if TYPE_CHECKING:
    from material_register.ui.settings.settings_widgets.summary_export_settings import (
        SummaryExportSettings,
    )


class SettingsController:
    def __init__(self, export_settings: "SummaryExportSettings") -> None:
        self.export_settings = export_settings
        self.settings = SettingsProvider.SETTINGS.get("export", {})

    def update_settings(self) -> None:
        user_settings = self.settings.get("summary", {}).get("user", {})
        new_data = self.export_settings.get_export_settings_data()
        if not user_settings or not new_data:
            SettingsController._handle_settings_error(
                "Update settings failed", f"{self.__class__.__name__}.update_settings"
            )
            return
        for key, value in new_data.items():
            if key in user_settings:
                user_settings[key] = value
        if not SettingsProvider.save_settings():
            SettingsController._handle_settings_error(
                "Update settings failed", f"{self.__class__.__name__}.update_settings"
            )
            return
        SettingsController._reload_settings()
        AppContext.MAIN_WINDOW.status_bar.show_message("SETTINGS_SAVED")

    def restore_settings(self) -> None:
        question = MessageBoxes.show_question(self.export_settings, "RESTORE_SETTINGS")
        if question:
            if not SettingsProvider.restore_settings("export", "summary"):
                SettingsController._handle_settings_error(
                    "Restore settings failed",
                    f"{self.__class__.__name__}.restore_settings",
                )
                return
            if not SettingsProvider.save_settings():
                SettingsController._handle_settings_error(
                    "Restore settings failed",
                    f"{self.__class__.__name__}.restore_settings",
                )
                return
            self.export_settings.apply_settings()
            self.export_settings.set_folder_path()
            SettingsController._reload_settings()
            AppContext.MAIN_WINDOW.status_bar.show_message("SETTINGS_RESTORED")

    @staticmethod
    def _reload_settings() -> None:
        stacked_widget = AppContext.MAIN_WINDOW.stacked_widget
        summary_export_widget = stacked_widget.export_widget.summary_export_widget
        if hasattr(summary_export_widget, "apply_settings"):
            summary_export_widget.apply_settings()

    @staticmethod
    def _handle_settings_error(error: str, method: str) -> None:
        if not error:
            error = f"Settings failed: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", "settings", "warning")
        dialog = ErrorDialog()
        dialog.show_dialog("SETTINGS_FAILED", False)
