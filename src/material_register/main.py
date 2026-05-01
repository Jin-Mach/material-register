import sys

from PySide6.QtWidgets import QApplication

from material_register.init.setup_init import SetupInit
from material_register.ui.dialogs.error_dialog import ErrorDialog
from src.material_register.init.app_init import AppInit
from src.material_register.ui.main_window import MainWindow


def run_app() -> None:
    app = QApplication(sys.argv)
    app_ok, app_error = AppInit.init_app()
    if not app_ok:
        dialog = ErrorDialog()
        dialog.show_dialog(app_error, False)
        sys.exit(1)
    setup_ok, setup_error = SetupInit.setup_init()
    if not setup_ok:
        dialog = ErrorDialog()
        dialog.show_dialog(setup_error, False)
        sys.exit(1)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()