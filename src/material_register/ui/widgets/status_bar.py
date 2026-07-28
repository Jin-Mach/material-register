from typing import TYPE_CHECKING

from PySide6.QtWidgets import QStatusBar, QLabel

from material_register.providers.texts_provider import TextsProvider

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class StatusBar(QStatusBar):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.status_texts = TextsProvider.STATUS_TEXTS
        self._create_ui()
        self._setup_texts()

    def _create_ui(self) -> None:
        self.permanent_label = QLabel()
        self.addWidget(self.permanent_label)

    def _setup_texts(self) -> None:
        if not self.status_texts:
            return
        self.permanent_label.setText(self.status_texts.get("READY", "Ready"))

    def show_message(self, key: str, timeout: int = 3000) -> None:
        if not self.status_texts:
            return
        self.showMessage(self.status_texts.get(key, ""), timeout)