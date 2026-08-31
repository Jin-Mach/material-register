from PySide6.QtWidgets import QApplication

from material_register.config.project_constants import (
    APPLICATION_NAME,
    ORGANIZATION_NAME,
)
from material_register.ui.setup.ui_icons import UiIcons
from material_register.ui.setup.ui_texts import UiTexts


class ApplicationSetup:
    APPLICATION = None

    @classmethod
    def setup_init(cls, application: QApplication) -> None:
        cls.APPLICATION = application
        cls._setup_info()

    @classmethod
    def _setup_info(cls) -> None:
        cls.APPLICATION.setApplicationName(APPLICATION_NAME)
        cls.APPLICATION.setOrganizationName(ORGANIZATION_NAME)

    @classmethod
    def setup_ui(cls) -> None:
        displayed_name = UiTexts.UI_TEXTS.get("Application", {}).get(
            "titleText", "Material Register"
        )
        if displayed_name:
            cls.APPLICATION.setApplicationDisplayName(displayed_name)
        if UiIcons.APPLICATION_ICON:
            cls.APPLICATION.setWindowIcon(UiIcons.APPLICATION_ICON)
