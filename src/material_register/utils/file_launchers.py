import os
import subprocess
import sys
from pathlib import Path

from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_APP,
)


def open_file_in_default(file_path: Path | str) -> bool:
    try:
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":
            subprocess.run(["open", file_path], check=True)
        else:
            subprocess.run(["xdg-open", file_path], check=True)
        return True
    except Exception as e:
        ErrorHandler.handle_error(e, LOGGER_APP, LOG_LEVEL_WARNING)
        return False


def open_file_in_explorer(file_path: Path | str) -> bool:
    try:
        path = os.path.abspath(file_path)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", path])
        elif sys.platform == "darwin":
            subprocess.run(["open", "-R", path], check=True)
        else:
            subprocess.run(["xdg-open", os.path.dirname(path)], check=True)
        return True
    except Exception as e:
        ErrorHandler.handle_error(e, LOGGER_APP, LOG_LEVEL_WARNING)
        return False
