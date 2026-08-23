from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from material_register.providers.texts_provider import TextsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.services.window_state_manager import WindowStateManager
from material_register.ui.dialogs.settings_widgets.settings_side_panel import (
    SettingsSidePanel,
)
from material_register.ui.dialogs.settings_widgets.settings_stacked_widget import (
    SettingsStackedWidget,
)
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.main_window import MainWindow


class SettingsDialog(QDialog):
    def __init__(self, main_window: "MainWindow") -> None:
        super().__init__(main_window)
        self.main_window = main_window
        self.status_texts = TextsProvider.STATUS_TEXTS
        self.setMinimumSize(900, 600)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        widgets_layout = QHBoxLayout()
        self.settings_side_panel = SettingsSidePanel(self)
        stacked_layout = QVBoxLayout()
        self.settings_stacked_widget = SettingsStackedWidget(self)
        buttons_layout = QHBoxLayout()
        self.info_label = QLabel()
        self.close_button = QPushButton()
        self.close_button.setObjectName("closeButton")
        buttons_layout.addWidget(self.info_label)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        stacked_layout.addWidget(self.settings_stacked_widget)
        stacked_layout.addLayout(buttons_layout)
        widgets_layout.addWidget(self.settings_side_panel)
        widgets_layout.addLayout(stacked_layout)
        main_layout.addLayout(widgets_layout)
        return main_layout

    def _setup_ui(self) -> None:
        if UiTexts.set_ui_texts(self, [self.close_button]):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, []):
            return

    def _create_connection(self):
        buttons_map = {self.settings_side_panel.export_button: 0}
        for button, index in buttons_map.items():
            button.clicked.connect(
                lambda _, i=index: self.settings_stacked_widget.setCurrentIndex(i)
            )
        self.close_button.clicked.connect(self.close)

    def set_info_text(self, key: str, time_sleep: int = 3000) -> None:
        if not self.status_texts:
            return
        self.info_label.setText(self.status_texts.get(key, ""))
        QTimer.singleShot(time_sleep, lambda: self.info_label.setText(""))

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if not WindowStateManager.load_geometry(self, self.__class__.__name__):
            screen = self.main_window.screen()
            geometry = screen.availableGeometry()
            frame = self.frameGeometry()
            frame.moveCenter(geometry.center())
            self.move(frame.topLeft())

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        WindowStateManager.save_geometry(self, self.__class__.__name__)
