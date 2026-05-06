import sys

from pathlib import Path

from material_register.services.error_handler import ErrorHandler


class PathsProvider:
    PROJECT_NAME = "material-register"

    root = None
    resources = None
    database = None
    logs = None

    @classmethod
    def paths_init(cls, log_structure: dict[str, tuple[str, str]]) -> None:
        cls.root = cls.get_base_path()
        if cls.root is None:
            return
        cls.resources = cls.root / "resources"
        cls.resources.mkdir(parents=True, exist_ok=True)
        cls.database = cls.root / "database"
        cls.database.mkdir(parents=True, exist_ok=True)
        cls.logs = cls.root / "logs"
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
                if parent.name == cls.PROJECT_NAME:
                    return parent
            return current.parents[3]
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return None