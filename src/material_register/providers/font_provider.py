from pathlib import Path

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class FontProvider:
    REGULAR = "DejaVuSans"
    BOLD = "DejaVuSans-Bold"

    @classmethod
    def provider_init(cls, resources_path: Path) -> None:
        cls._register_fonts(resources_path)

    @classmethod
    def _register_fonts(cls, resources_path: Path) -> None:
        pdfmetrics.registerFont(
            TTFont(cls.REGULAR, resources_path / "fonts" / f"{cls.REGULAR}.ttf")
        )
        pdfmetrics.registerFont(
            TTFont(cls.BOLD, resources_path / "fonts" / f"{cls.BOLD}.ttf")
        )
