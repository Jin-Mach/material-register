from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStatusBar

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class StatusBar(QStatusBar):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)

    def show_message(self, message: str, timeout: int = 3000) -> None:
        self.showMessage(message, timeout)