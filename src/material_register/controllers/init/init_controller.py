import sys
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, QObject, QTimer

from material_register.ui.main_window import MainWindow
from material_register.ui.dialogs.error_dialog import ErrorDialog
from material_register.workers.init.init_worker import InitWorker

if TYPE_CHECKING:
    from material_register.ui.widgets.splash_screen import SplashScreen


class InitController(QObject):

    def __init__(self, splash_screen: "SplashScreen") -> None:
        super().__init__()
        self.splash_screen = splash_screen
        self.main_window = None
        self.thread = None
        self.worker = None

    def start_thread(self) -> None:
        self.splash_screen.show_splash()
        QTimer.singleShot(1000, self._start_worker)

    def _start_worker(self) -> None:
        self.thread = QThread()
        self.worker = InitWorker()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.error_signal.connect(self.init_error)
        self.worker.finished_signal.connect(self.init_ok)
        self.thread.start()

    def init_error(self, error: str) -> None:
        self.clean_thread(True)
        self.splash_screen.close()
        dialog = ErrorDialog()
        dialog.show_dialog(error, False)
        sys.exit(1)

    def init_ok(self) -> None:
        self.clean_thread(False)
        self.splash_screen.close()
        self.main_window = MainWindow()
        self.main_window.show()

    def clean_thread(self, reset_main_window: bool) -> None:
        self.thread.quit()
        self.thread.wait()
        self.worker.deleteLater()
        self.thread.deleteLater()
        self.thread = None
        self.worker = None
        if reset_main_window:
            self.main_window = None