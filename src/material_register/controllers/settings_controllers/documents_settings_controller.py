from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from material_register.providers.settings_provider import SettingsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog
    from material_register.ui.settings.settings_documents_widget import (
        SettingsDocumentsWidget,
    )


class DocumentsSettingsController:
    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        self.settings_dialog = settings_dialog
        self.settings = SettingsProvider.SETTINGS.get("export", {}).get("documents", {})

    def update_settings(self, documents_widget: "SettingsDocumentsWidget") -> None:
        user_settings = self.settings.get("user", {})
        new_data = documents_widget.get_documents_settings_data()
        if not user_settings or not new_data:
            self._handle_settings_error(
                "Update settings failed",
                f"{self.__class__.__name__}.update_settings",
                self.settings_dialog,
            )
            return
        for key, value in new_data.items():
            if key in user_settings:
                user_settings[key] = value
        if not SettingsProvider.save_settings():
            self._handle_settings_error(
                "Update settings failed",
                f"{self.__class__.__name__}.update_settings",
                self.settings_dialog,
            )
            return
        self.settings_dialog.set_info_text("SETTINGS_SAVED")

    def restore_settings(self, documents_widget: "SettingsDocumentsWidget") -> None:
        question = MessageBoxes.show_question(
            documents_widget,
            "RESTORE_SETTINGS",
        )
        if not question:
            return
        if not SettingsProvider.restore_settings("export", "documents"):
            self._handle_settings_error(
                "Restore settings failed",
                f"{self.__class__.__name__}.restore_settings",
                self.settings_dialog,
            )
            return
        if not SettingsProvider.save_settings():
            self._handle_settings_error(
                "Restore settings failed",
                f"{self.__class__.__name__}.restore_settings",
                self.settings_dialog,
            )
            return
        documents_widget.apply_settings()
        documents_widget.set_folder_path()
        self.settings = SettingsProvider.SETTINGS.get("export", {}).get("documents", {})
        self.settings_dialog.set_info_text("SETTINGS_RESTORED")

    @staticmethod
    def _handle_settings_error(error: str, method: str, parent: QWidget) -> None:
        if not error:
            error = f"Settings failed: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", "settings", "warning")
        ErrorDialog(parent).show_dialog("SETTINGS_FAILED", False)
