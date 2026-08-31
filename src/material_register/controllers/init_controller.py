import sys
from pathlib import Path

from PySide6.QtCore import QObject, QThread, QTimer
from PySide6.QtWidgets import QApplication

from material_register.core.app_context import AppContext
from material_register.core.application_setup import ApplicationSetup
from material_register.providers.style_provider import StyleProvider
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.ui.main_window import MainWindow
from material_register.ui.widgets.splash_screen import SplashScreen
from material_register.workers.init_worker import InitWorker


class InitController(QObject):
    def __init__(self, resources_path: Path, application: QApplication) -> None:
        super().__init__()
        self.splash_screen = SplashScreen(resources_path)
        StyleProvider.provider_init(application, resources_path)
        self.main_window = None
        self.thread = None
        self.worker = None

    def start_thread(self) -> None:
        self.splash_screen.show_splash()
        QTimer.singleShot(0, self._start_worker)

    def _start_worker(self) -> None:
        self.thread = QThread()
        self.worker = InitWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error.connect(self._init_error)
        self.worker.finished.connect(self._init_ok)
        self.thread.start()

    def _init_error(self, error: str) -> None:
        self._clean_thread(True)
        QTimer.singleShot(1000, lambda: self._finish_error(error))

    def _init_ok(self) -> None:
        self._clean_thread(False)
        QTimer.singleShot(1000, self._finish_ok)

    def _finish_ok(self) -> None:
        self.splash_screen.close()
        ApplicationSetup.setup_ui()
        self.main_window = MainWindow()
        AppContext.set_main_window(self.main_window)
        StyleProvider.apply_style()
        self.main_window.show()

    def _finish_error(self, error: str) -> None:
        self.splash_screen.close()
        dialog = ErrorDialog()
        dialog.show_dialog(error, False)
        sys.exit(1)

    def _clean_thread(self, reset_main_window: bool) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.thread = None
        self.worker = None
        if reset_main_window:
            self.main_window = None
