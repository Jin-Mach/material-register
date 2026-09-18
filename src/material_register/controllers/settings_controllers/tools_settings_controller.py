from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from material_register.controllers.tools_controllers.cash_balance_controller import (
    CashBalanceController,
)
from material_register.providers.settings_provider import SettingsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.message_boxes import MessageBoxes

if TYPE_CHECKING:
    from material_register.ui.settings.settings_tools_widget import SettingsToolsWidget
    from material_register.ui.tools.right_toolbar_widget import RightToolbarWidget


class ToolsSettingsController:
    def __init__(
        self,
        settings_tools_widget: "SettingsToolsWidget",
    ) -> None:
        super().__init__()
        self.settings_tools_widget = settings_tools_widget
        self.settings_dialog = settings_tools_widget.settings_dialog
        self.settings = SettingsProvider.SETTINGS.get("tools", {})

    def update_tools_settings(self) -> None:
        user_settings = self.settings.get("settings", {}).get("user", {})
        new_data = self.settings_tools_widget.get_tools_settings_data()
        if not user_settings or not new_data:
            self._handle_settings_error(
                "Update settings failed",
                f"{self.__class__.__name__}.update_tools_settings",
                self.settings_dialog,
            )
            return
        for key, value in new_data.items():
            if key in user_settings:
                user_settings[key] = value
        if not SettingsProvider.save_settings():
            self._handle_settings_error(
                "Update settings failed",
                f"{self.__class__.__name__}.update_tools_settings",
                self.settings_dialog,
            )
            return
        self.settings_dialog.set_info_text("SETTINGS_SAVED")

    def restore_tools_settings(self) -> None:
        question = MessageBoxes.show_question(
            self.settings_tools_widget,
            "RESTORE_SETTINGS",
        )
        if not question:
            return
        if not SettingsProvider.restore_settings("tools", "settings"):
            self._handle_settings_error(
                "Restore settings failed",
                f"{self.__class__.__name__}.restore_tools_settings",
                self.settings_dialog,
            )
            return
        if not SettingsProvider.save_settings():
            self._handle_settings_error(
                "Restore settings failed",
                f"{self.__class__.__name__}.restore_tools_settings",
                self.settings_dialog,
            )
            return
        self.settings_tools_widget.apply_settings()
        self.settings_dialog.set_info_text("SETTINGS_RESTORED")

    @staticmethod
    def save_tools(
        splitter_size: int, right_toolbar_widget: "RightToolbarWidget"
    ) -> None:
        ToolsSettingsController._save_splitter(splitter_size)
        ToolsSettingsController._save_cash_tools(right_toolbar_widget)
        right_toolbar_widget.notes_widget.notes_controller.save_notes()

    @staticmethod
    def _save_splitter(splitter_size: int) -> None:
        tools_settings = ToolsSettingsController._get_tools_user_settings()
        splitter_settings = (
            SettingsProvider.SETTINGS.get("tools", {})
            .get("right_toolbar_panel", {})
            .get("user", {})
        )
        if tools_settings.get("containerSizeCheckbox", True):
            splitter_settings["splitterWidth"] = splitter_size

    @staticmethod
    def _save_cash_tools(right_toolbar_widget: "RightToolbarWidget") -> None:
        tools_settings = ToolsSettingsController._get_tools_user_settings()
        values_save = tools_settings.get("valuesCashCheckbox", True)
        others_save = tools_settings.get("othersCashCheckbox", False)
        CashBalanceController.save_balance_values(
            right_toolbar_widget.cash_balance_widget.get_values_map(),
            values_save=values_save,
            others_save=others_save,
        )

    @staticmethod
    def _get_tools_user_settings() -> dict[str, bool]:
        return (
            SettingsProvider.SETTINGS.get("tools", {})
            .get("settings", {})
            .get("user", {})
        )

    @staticmethod
    def _handle_settings_error(error: str, method: str, parent: QWidget) -> None:
        if not error:
            error = f"Settings failed: {method}"
        ErrorHandler.handle_error(f"{error}: {method}", "settings", "warning")
        ErrorDialog(parent).show_dialog("SETTINGS_FAILED", False)
