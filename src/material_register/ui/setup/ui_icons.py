from pathlib import Path

from PySide6.QtGui import QIcon


class UiIcons:
    IMAGES_PATH = None
    ACTIVE_ICON = None
    INACTIVE_ICON = None

    @classmethod
    def setup_init(cls, resources_path: Path) -> None:
        cls.IMAGES_PATH = resources_path / "images"
        cls.ACTIVE_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "activeIcon.png"))
        cls.INACTIVE_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "inactiveIcon.png"))
