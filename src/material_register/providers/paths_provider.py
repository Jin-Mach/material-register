import sys

from pathlib import Path

from PySide6.QtCore import QStandardPaths

from material_register.config.project_constants import PROJECT_NAME
from material_register.services.error_handler import ErrorHandler


class PathsProvider:
    root = None
    resources = None
    database = None
    logs = None

    @classmethod
    def paths_init(cls, log_structure: dict[str, tuple[str, str]]) -> None:
        if all([cls.root, cls.resources, cls.database, cls.logs]):
            return
        cls.root = cls.get_base_path()
        if cls.root is None:
            return
        cls.resources = cls.root / "resources"
        cls.resources.mkdir(parents=True, exist_ok=True)
        if getattr(sys, "frozen", False) or "__compiled__" in globals():
            app_data_dir = Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppLocalDataLocation))
            cls.database = app_data_dir / "database"
            cls.logs = app_data_dir / "logs"
        else:
            cls.database = cls.root / "database"
            cls.logs = cls.root / "logs"
        cls.database.mkdir(parents=True, exist_ok=True)
        cls.logs.mkdir(parents=True, exist_ok=True)
        for folder, _ in log_structure.values():
            (cls.logs / folder).mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_base_path(cls) -> Path | None:
        try:
            exe = Path(sys.executable).resolve()
            current = Path(__file__).resolve()
            if getattr(sys, "frozen", False) or "__compiled__" in globals():
                return exe.parent
            for parent in current.parents:
                if parent.name == PROJECT_NAME:
                    return parent
            return current.parents[3]
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return None