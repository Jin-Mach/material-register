import sys

from PySide6.QtWidgets import QApplication

from material_register.controllers.init.init_controller import InitController
from material_register.ui.widgets.splash_screen import SplashScreen


def run_app() -> None:
    app = QApplication(sys.argv)
    splash_screen = SplashScreen()
    init_controller = InitController(splash_screen)
    init_controller.start_thread()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()