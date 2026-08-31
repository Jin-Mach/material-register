from typing import TYPE_CHECKING

from material_register.config.ui_constants import (
    EXPORT_TYPE_SUMMARY,
    EXPORT_TYPE_TRANSACTIONS,
)
from material_register.providers.settings_provider import SettingsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog
    from material_register.ui.settings.settings_widgets.base_export_widget import (
        BaseExportWidget,
    )


class ExportSettingsController:
    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        self.settings_dialog = settings_dialog
        self.summary_export_widget = settings_dialog.main_window.stacked_widget.export_widget.summary_export_widget
        self.transactions_export_widget = settings_dialog.main_window.stacked_widget.export_widget.transactions_export_widget
        self.settings = SettingsProvider.SETTINGS.get("export", {})

    def update_summary_settings(
        self, export_type: str, export_widget: "BaseExportWidget"
    ) -> None:
        export_settings = export_widget
        user_settings = self.settings.get(export_type, {}).get("user", {})
        new_data = export_settings.get_export_settings_data()
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
        if not self._reload_settings(export_type):
            return
        self.settings_dialog.set_info_text("SETTINGS_SAVED")

    def restore_summary_settings(
        self, export_type: str, export_widget: "BaseExportWidget"
    ) -> None:
        export_settings = export_widget
        question = MessageBoxes.show_question(
            export_settings,
            "RESTORE_SETTINGS",
        )
        if not question:
            return
        if not SettingsProvider.restore_settings("export", export_type):
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
        export_settings.apply_settings()
        export_settings.set_folder_path()
        if not self._reload_settings(export_type):
            return
        self.settings_dialog.set_info_text("SETTINGS_RESTORED")

    def _reload_settings(self, export_type: str) -> bool:
        export_map = {
            EXPORT_TYPE_SUMMARY: self.summary_export_widget,
            EXPORT_TYPE_TRANSACTIONS: self.transactions_export_widget,
        }
        export_widget = export_map.get(export_type, None)
        if export_widget is None:
            return False
        if hasattr(export_widget, "apply_settings"):
            export_widget.apply_settings()
            return True
        return False

    @staticmethod
    def _handle_settings_error(error: str, method: str) -> None:
        if not error:
            error = f"Settings failed: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", "settings", "warning")
        dialog = ErrorDialog()
        dialog.show_dialog("SETTINGS_FAILED", False)
