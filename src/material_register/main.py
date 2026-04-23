import sys

from PySide6.QtWidgets import QApplication

from material_register.init.setup_init import SetupInit
from src.material_register.init.app_init import AppInit
from src.material_register.ui.main_window import MainWindow


def run_app() -> None:
    app = QApplication(sys.argv)
    if not AppInit.init_app():
        sys.exit(1)
    if not SetupInit.setup_init():
        sys.exit(1)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()