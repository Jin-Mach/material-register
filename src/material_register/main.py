import sys

from PySide6.QtWidgets import QApplication

from material_register.config.logging_congig import LOG_STRUCTURE
from material_register.controllers.init_controller import InitController
from material_register.providers.paths_provider import PathsProvider


def run_app() -> None:
    app = QApplication(sys.argv)
    PathsProvider.paths_init(LOG_STRUCTURE)
    init_controller = InitController(PathsProvider.resources)
    init_controller.start_thread()
    sys.exit(app.exec())

if __name__ == "__main__":
    run_app()