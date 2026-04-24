import sys
from pathlib import Path


class RootProvider:
    PROJECT_NAME = "material-register"
    root = None
    resources = None

    @classmethod
    def paths_init(cls):
        cls.root = cls.get_base_path()
        cls.resources = cls.root / "resources"
        cls.resources.mkdir(parents=True, exist_ok=True)

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
            print(f"PathsProvider error: {e}")
            return None