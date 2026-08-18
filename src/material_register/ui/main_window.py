from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QWidget

from material_register.services.error_handler import ErrorHandler
from material_register.services.settings_manager import SettingsManager
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.widgets.side_panel import SidePanel
from material_register.ui.widgets.stacked_widget import StackedWidget
from material_register.ui.widgets.status_bar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(900, 600)
        self.setCentralWidget(self._create_ui())
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)
        self._setup_ui()
        self._create_connection()
        self.settings_manager = SettingsManager(self)

    def _create_ui(self) -> QWidget:
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.side_panel = SidePanel(self)
        self.stacked_widget = StackedWidget(self)
        main_layout.addWidget(self.side_panel)
        main_layout.addWidget(self.stacked_widget)
        central_widget.setLayout(main_layout)
        return central_widget

    def _setup_ui(self) -> None:
        if UiTexts.set_ui_texts(self, []):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}", "ui", "warning"
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        if UiTexts.set_default_texts(self, []):
            return

    def _create_connection(self) -> None:
        buttons_map = {
            self.side_panel.transactions_button: 0,
            self.side_panel.inventory_button: 1,
            self.side_panel.export_button: 2,
            self.side_panel.customers_button: 3,
            self.side_panel.catalog_button: 4,
            self.side_panel.settings_button: 5,
        }
        for button, index in buttons_map.items():
            button.clicked.connect(
                lambda _, i=index: self.stacked_widget.setCurrentIndex(i)
            )

    @staticmethod
    def _handle_startup_errors() -> None:
        error = ErrorHandler.ui_texts_error
        if error != "":
            ErrorDialog().show_dialog(error, False)
            ErrorHandler.ui_texts_error = ""

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if not self.settings_manager.load_settings():
            screen = self.screen()
            geometry = screen.availableGeometry()
            frame = self.frameGeometry()
            frame.moveCenter(geometry.center())
            self.move(frame.topLeft())
        MainWindow._handle_startup_errors()

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        self.settings_manager.save_settings()
