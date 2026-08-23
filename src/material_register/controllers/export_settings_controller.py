from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from material_register.providers.settings_provider import SettingsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class ExportSettingsController:
    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        self.settings_dialog = settings_dialog
        self.summary_export_widget = settings_dialog.main_window.stacked_widget.export_widget.summary_export_widget
        self.settings = SettingsProvider.SETTINGS.get("export", {})

    def update_summary_settings(self) -> None:
        summary_export_settings = self.settings_dialog.settings_stacked_widget.settings_export_widget.summary_export_settings
        user_settings = self.settings.get("summary", {}).get("user", {})
        new_data = summary_export_settings.get_export_settings_data()
        if not user_settings or not new_data:
            self._handle_settings_error(
                "Update settings failed",
                f"{self.__class__.__name__}.update_summary_settings",
            )
            return
        for key, value in new_data.items():
            if key in user_settings:
                user_settings[key] = value
        if not SettingsProvider.save_settings():
            self._handle_settings_error(
                "Update settings failed",
                f"{self.__class__.__name__}.update_summary_settings",
            )
            return
        ExportSettingsController._reload_settings(self.summary_export_widget)
        self.settings_dialog.set_info_text("SETTINGS_SAVED")

    def restore_summary_settings(self) -> None:
        summary_export_settings = self.settings_dialog.settings_stacked_widget.settings_export_widget.summary_export_settings
        question = MessageBoxes.show_question(
            summary_export_settings,
            "RESTORE_SETTINGS",
        )
        if not question:
            return
        if not SettingsProvider.restore_settings("export", "summary"):
            self._handle_settings_error(
                "Restore settings failed",
                f"{self.__class__.__name__}.restore_summary_settings",
            )
            return
        if not SettingsProvider.save_settings():
            self._handle_settings_error(
                "Restore settings failed",
                f"{self.__class__.__name__}.restore_summary_settings",
            )
            return
        summary_export_settings.apply_settings()
        summary_export_settings.set_folder_path()
        ExportSettingsController._reload_settings(self.summary_export_widget)
        self.settings_dialog.set_info_text("SETTINGS_RESTORED")

    @staticmethod
    def _reload_settings(export_widget: QWidget) -> None:
        if hasattr(export_widget, "apply_settings"):
            export_widget.apply_settings()

    @staticmethod
    def _handle_settings_error(error: str, method: str) -> None:
        if not error:
            error = f"Settings failed: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", "settings", "warning")
        dialog = ErrorDialog()
        dialog.show_dialog("SETTINGS_FAILED", False)
