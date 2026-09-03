from PySide6.QtGui import QCloseEvent, QShowEvent
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QScrollArea, QWidget

from material_register.controllers.tools_controllers.cash_balance_controller import (
    CashBalanceController,
)
from material_register.providers.settings_provider import SettingsProvider
from material_register.services.error_handler import ErrorHandler
from material_register.services.window_state_manager import WindowStateManager
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.dialogs.settings_dialog import SettingsDialog
from material_register.ui.setup.ui_texts import UiTexts
from material_register.ui.tools.right_toolbar_widget import RightToolbarWidget
from material_register.ui.widgets.side_panel import SidePanel
from material_register.ui.widgets.stacked_widget import StackedWidget
from material_register.ui.widgets.status_bar import StatusBar


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumSize(900, 600)
        self.status_bar = StatusBar(self)
        self.setStatusBar(self.status_bar)
        self.setCentralWidget(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QWidget:
        central_widget = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        self.side_panel = SidePanel(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.stacked_widget = StackedWidget(self)
        self.right_toolbar_widget = RightToolbarWidget(self)
        self.scroll_area.setWidget(self.stacked_widget)
        main_layout.addWidget(self.side_panel)
        main_layout.addWidget(self.scroll_area, 1)
        main_layout.addWidget(self.right_toolbar_widget)
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
        }
        for button, index in buttons_map.items():
            button.clicked.connect(
                lambda _, i=index: self.stacked_widget.setCurrentIndex(i)
            )
        self.side_panel.settings_button.clicked.connect(self._show_settings_dialog)

    def _show_settings_dialog(self) -> None:
        self.settings_dialog = SettingsDialog(self)
        self.settings_dialog.exec()

    def _handle_startup_errors(self) -> None:
        error = ErrorHandler.ui_texts_error
        if error != "":
            ErrorDialog(self).show_dialog(error, False)
            ErrorHandler.ui_texts_error = ""

    def _before_close(self) -> None:
        CashBalanceController.save_balance_values(
            self.right_toolbar_widget.cash_balance_widget.get_values_map()
        )
        SettingsProvider.save_settings()
        self.right_toolbar_widget.notes_widget.notes_controller.save_notes()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if not WindowStateManager.load_geometry(self, self.__class__.__name__):
            screen = self.screen()
            geometry = screen.availableGeometry()
            frame = self.frameGeometry()
            frame.moveCenter(geometry.center())
            self.move(frame.topLeft())
        self._handle_startup_errors()

    def closeEvent(self, event: QCloseEvent) -> None:
        super().closeEvent(event)
        self._before_close()
        WindowStateManager.save_geometry(self, self.__class__.__name__)
