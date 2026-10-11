from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QTreeWidgetItem, QWidget


class UiIcons:
    IMAGES_PATH: Path | None = None
    APPLICATION_ICON: QIcon | None = None
    ACTIVE_ICON: QIcon | None = None
    INACTIVE_ICON: QIcon | None = None
    COPY_ICON: QIcon | None = None
    DELETE_ICON: QIcon | None = None
    OPEN_FOLDER_ICON: QIcon | None = None
    CLOSE_FOLDER_ICON: QIcon | None = None
    DATABASE_ICON: QIcon | None = None
    ITEM_ICON: QIcon | None = None
    PRINT_ICON: QIcon | None = None
    SAVE_ICON: QIcon | None = None
    ZOOM_IN_ICON: QIcon | None = None
    ZOOM_OUT_ICON: QIcon | None = None
    ZOOM_RESET_ICON: QIcon | None = None

    # icons color: #FFE066
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
        cls.OPEN_FOLDER_ICON = QIcon(
            str(cls.IMAGES_PATH / "ui_icons" / "openFolderIcon.png")
        )
        cls.CLOSE_FOLDER_ICON = QIcon(
            str(cls.IMAGES_PATH / "ui_icons" / "closeFolderIcon.png")
        )
        cls.DATABASE_ICON = QIcon(
            str(cls.IMAGES_PATH / "ui_icons" / "databaseIcon.png")
        )
        cls.ITEM_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "itemIcon.png"))
        cls.PRINT_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "printIcon.png"))
        cls.SAVE_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "saveIcon.png"))
        cls.ZOOM_IN_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "zoomInIcon.png"))
        cls.ZOOM_OUT_ICON = QIcon(str(cls.IMAGES_PATH / "ui_icons" / "zoomOutIcon.png"))
        cls.ZOOM_RESET_ICON = QIcon(
            str(cls.IMAGES_PATH / "ui_icons" / "zoomResetIcon.png")
        )

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

    @classmethod
    def set_tree_widget_icon(
        cls, item: QTreeWidgetItem, expanded: bool = False
    ) -> None:
        if expanded:
            item.setIcon(0, cls.OPEN_FOLDER_ICON)
        else:
            item.setIcon(0, cls.CLOSE_FOLDER_ICON)
