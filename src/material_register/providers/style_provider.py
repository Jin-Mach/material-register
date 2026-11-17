import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication


class StyleProvider:
    APPLICATION_INSTANCE: QApplication | None = None
    STYLE_PATH: Path | None = None
    IMAGES_PATH: Path | None = None
    DARK_BLUE = "dark_blue"

    @classmethod
    def provider_init(cls, application: QApplication, resources_path: Path) -> None:
        cls.APPLICATION_INSTANCE = application
        cls.STYLE_PATH = resources_path / "styles"
        cls.IMAGES_PATH = resources_path / "images"

    @classmethod
    def apply_style(cls, style_name: str = DARK_BLUE) -> None:
        style_path = (cls.STYLE_PATH / style_name).with_suffix(".qss")
        if not style_path.exists():
            return
        if sys.platform == "win32":
            cls.APPLICATION_INSTANCE.setStyle("Fusion")
        with style_path.open("r", encoding="utf-8") as style_file:
            stylesheet = style_file.read()
        icons_path = (cls.IMAGES_PATH / "ui_icons").resolve()
        stylesheet = StyleProvider._set_widgets_icons(stylesheet, icons_path)
        cls.APPLICATION_INSTANCE.setStyleSheet(stylesheet)

    @staticmethod
    def _set_widgets_icons(stylesheet: str, icons_path: Path) -> str:
        icons_map = {
            "{CHECK_ICON}": "checkedIcon.png",
            "{COMBO_ARROW}": "comboArrowIcon.png",
            "{CALENDAR_ICON}": "calendarIcon.png",
            "{SPINBOX_UP_ICON}": "spinboxUpArrow.png",
            "{SPINBOX_DOWN_ICON}": "spinboxDownArrow.png",
            "{DOUBLE_SPINBOX_UP_ICON}": "doubleSpinboxUpArrow",
            "{DOUBLE_SPINBOX_DOWN_ICON}": "doubleSpinboxDownArrow",
        }
        for placeholder, icon_name in icons_map.items():
            stylesheet = stylesheet.replace(
                placeholder, (icons_path / icon_name).as_posix()
            )
        return stylesheet
