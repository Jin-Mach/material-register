from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QWidget

from material_register.config.project_constants import (
    APPLICATION_NAME,
    ORGANIZATION_NAME,
)


class WindowStateManager:
    _settings = QSettings(ORGANIZATION_NAME, APPLICATION_NAME)

    @classmethod
    def save_geometry(cls, window: QWidget, key: str) -> None:
        settings_key = f"windows/{key}/geometry"
        cls._settings.setValue(settings_key, window.saveGeometry())

    @classmethod
    def load_geometry(cls, window: QWidget, key: str) -> bool:
        settings_key = f"windows/{key}/geometry"
        if not cls._settings.contains(settings_key):
            return False
        window.restoreGeometry(cls._settings.value(settings_key))
        return True
