from PySide6.QtWidgets import QWidget

from material_register.config.ui_defaults import DEFAULT_TEXTS


# noinspection PyBroadException
class UiTexts:
    UI_TEXTS = {}

    @classmethod
    def setup_init(cls, ui_texts: dict[str, dict[str, str]]) -> None:
        cls.UI_TEXTS = ui_texts.copy()

    @classmethod
    def set_ui_texts(
        cls, parent: QWidget, widgets: list[QWidget], tooltip_duration: int = 5000
    ) -> bool:
        try:
            ui_texts = cls.UI_TEXTS.get(parent.__class__.__name__, {})
            if not ui_texts:
                return False
            return UiTexts.set_texts(ui_texts, parent, widgets, tooltip_duration)
        except Exception:
            return False

    @staticmethod
    def set_default_texts(
        parent: QWidget, widgets: list[QWidget], tooltip_duration: int = 5000
    ) -> bool:
        try:
            ui_texts = DEFAULT_TEXTS.get(parent.__class__.__name__, {})
            if not ui_texts:
                return False
            return UiTexts.set_texts(ui_texts, parent, widgets, tooltip_duration)
        except Exception:
            return False

    @staticmethod
    def set_texts(
        ui_texts: dict[str, str],
        parent: QWidget,
        widgets: list[QWidget],
        tooltip_duration: int = 5000,
    ) -> bool:
        try:
            if hasattr(parent, "setWindowTitle") and "titleText" in ui_texts:
                parent.setWindowTitle(ui_texts["titleText"])
            for widget in widgets:
                name = widget.objectName()
                text = name + "Text"
                tooltip = name + "TooltipText"
                placeholder = name + "PlaceholderText"
                if hasattr(widget, "setTitle") and text in ui_texts:
                    widget.setTitle(ui_texts[text])
                if hasattr(widget, "setText") and text in ui_texts:
                    widget.setText(ui_texts[text])
                if hasattr(widget, "setToolTip") and tooltip in ui_texts:
                    widget.setToolTip(ui_texts[tooltip])
                    widget.setToolTipDuration(tooltip_duration)
                if hasattr(widget, "setPlaceholderText") and placeholder in ui_texts:
                    widget.setPlaceholderText(ui_texts[placeholder])
            return True
        except Exception:
            return False
