from pathlib import Path

from PySide6.QtWidgets import QApplication


class StyleProvider:
    APPLICATION_INSTANCE = None
    STYLE_PATH = None
    DARK_BLUE = "dark_blue"

    @classmethod
    def provider_init(cls, application: QApplication, resources_path: Path) -> None:
        cls.APPLICATION_INSTANCE = application
        cls.STYLE_PATH = resources_path / "styles"

    @classmethod
    def apply_style(cls, style_name: str = DARK_BLUE) -> None:
        style_path = (cls.STYLE_PATH / style_name).with_suffix(".qss")
        if not style_path.exists():
            return
        with style_path.open("r", encoding="utf-8") as style_file:
            cls.APPLICATION_INSTANCE.setStyleSheet(style_file.read())