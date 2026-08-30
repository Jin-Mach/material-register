import sys

from PySide6.QtWidgets import QApplication

from material_register.config.logging_config import LOG_STRUCTURE
from material_register.config.project_constants import APPLICATION_NAME, ORGANIZATION_NAME
from material_register.controllers.init_controller import InitController
from material_register.providers.lock_provider import LockProvider
from material_register.providers.paths_provider import PathsProvider


def run_app() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(APPLICATION_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    PathsProvider.paths_init(LOG_STRUCTURE)
    if not LockProvider.setup_lock():
        sys.exit(0)
    init_controller = InitController(PathsProvider.resources, app)
    init_controller.start_thread()
    try:
        sys.exit(app.exec())
    finally:
        LockProvider.unlock_app()


if __name__ == "__main__":
    run_app()
