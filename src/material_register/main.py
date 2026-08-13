import sys

from PySide6.QtWidgets import QApplication

from material_register.config.logging_config import LOG_STRUCTURE
from material_register.controllers.init_controller import InitController
from material_register.providers.paths_provider import PathsProvider

APPLICATION_NAME = "MaterialRegister"
ORGANIZATION_NAME = "Jin-Mach"


def run_app() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    PathsProvider.paths_init(LOG_STRUCTURE)
    init_controller = InitController(PathsProvider.resources, app)
    init_controller.start_thread()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
