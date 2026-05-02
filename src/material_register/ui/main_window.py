from PySide6.QtGui import QShowEvent, QCloseEvent
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout

from material_register.services.settings_manager import SettingsManager
from material_register.ui.dialogs.error_dialog import ErrorDialog
from src.material_register.ui.setup.ui_texts import UiTexts
from src.material_register.ui.widgets.side_panel import SidePanel
from src.material_register.ui.widgets.stacked_widget import StackedWidget


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(900, 600)
        self.setCentralWidget(self._create_ui())
        self._ui_setup()
        self._create_connection()
        self.settings_manager = SettingsManager(self)

    def _create_ui(self) -> QWidget:
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        self.side_panel = SidePanel(self)
        self.stacked_widget = StackedWidget(self)
        main_layout.addWidget(self.side_panel)
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        return central_widget

    def _ui_setup(self) -> None:
        if not UiTexts.set_ui_texts(self, []):
            dialog = ErrorDialog()
            dialog.show_dialog("TEXTS_LOAD_FAILED", False)

    def _create_connection(self) -> None:
        buttons_map = {
            self.stacked_widget.register_widget.actions_widget.add_action_button: 0
        }
        for button, index in buttons_map.items():
            button.clicked.connect(lambda i=index: self.stacked_widget.setCurrentIndex(i))

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if not self.settings_manager.load_settings():
            screen = self.screen()
            geometry = screen.availableGeometry()
            frame = self.frameGeometry()
            frame.moveCenter(geometry.center())
            self.move(frame.topLeft())

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        self.settings_manager.save_settings()