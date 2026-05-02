from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QSettings

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class SettingsManager(QObject):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings("Jin-Mach", "material_register")

    def save_settings(self) -> None:
        geometry = self.main_window.saveGeometry()
        self.settings.setValue("geometry", geometry)

    def load_settings(self) -> bool:
        if self.settings.contains("geometry"):
            self.main_window.restoreGeometry(self.settings.value("geometry"))
            return True
        return False