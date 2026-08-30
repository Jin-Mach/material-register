from pathlib import Path

from PySide6.QtCore import QLockFile, QStandardPaths

from material_register.config.project_constants import (
    LOCK_FILE_NAME,
    ORGANIZATION_NAME,
    PROJECT_NAME,
)


class LockProvider:
    _lock_path = (
        Path(
            QStandardPaths.writableLocation(
                QStandardPaths.StandardLocation.AppLocalDataLocation
            )
        )
        / ORGANIZATION_NAME
        / PROJECT_NAME
        / "lock"
    )
    _lock_path.mkdir(parents=True, exist_ok=True)
    _lock = QLockFile(str(_lock_path / LOCK_FILE_NAME))
    _lock.setStaleLockTime(0)

    @classmethod
    def setup_lock(cls) -> bool:
        return cls._lock.tryLock(100)

    @classmethod
    def unlock_app(cls) -> None:
        cls._lock.unlock()
