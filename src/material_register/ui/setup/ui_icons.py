from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget


class UiIcons:
    IMAGES_PATH = None
    APPLICATION_ICON = None
    ACTIVE_ICON = None
    INACTIVE_ICON = None
    COPY_ICON = None
    DELETE_ICON = None

    @classmethod
    def setup_init(cls, resources_path: Path) -> None:
        cls.IMAGES_PATH = resources_path / "images"
        cls.APPLICATION_ICON = QIcon(
            str(cls.IMAGES_PATH / "system" / "applicationIcon.png")
        )
        cls.ACTIVE_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "activeIcon.png"))
        cls.INACTIVE_ICON = QIcon(
            str(cls.IMAGES_PATH / "ui_icons" / "inactiveIcon.png")
        )
        cls.COPY_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "copyIcon.png"))
        cls.DELETE_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "deleteIcon.png"))

    @classmethod
    def set_icons(
        cls, icons_dir: str, widgets: list[QWidget], icon_size: int = 24
    ) -> bool:
        supported_dirs = ["tools"]
        if not cls.IMAGES_PATH.exists():
            return False
        if not icons_dir in supported_dirs:
            return False
        for widget in widgets:
            if hasattr(widget, "setIcon"):
                icon = (
                    cls.IMAGES_PATH
                    / f"{icons_dir}_icons"
                    / f"{widget.objectName()}Icon.png"
                )
                if icon.exists():
                    widget.setIcon(QIcon(str(icon)))
                    widget.setIconSize(QSize(icon_size, icon_size))
        return True
