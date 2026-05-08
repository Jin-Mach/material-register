from PySide6.QtWidgets import QWidget

from material_register.services.error_handler import ErrorHandler


class UiTexts:
    UI_TEXTS = {}

    @classmethod
    def setup_init(cls, ui_texts):
        cls.UI_TEXTS = ui_texts.copy()

    @classmethod
    def set_ui_texts(cls, parent: QWidget, widgets: list[QWidget], tooltip_duration: int = 5000) -> bool:
        try:
            ui_texts = cls.UI_TEXTS.get(parent.__class__.__name__, {})
            if not ui_texts:
                return False
            if hasattr(parent, "setWindowTitle") and "titleText" in ui_texts:
                parent.setWindowTitle(ui_texts["titleText"])
            for widget in widgets:
                name = widget.objectName()
                text = name + "Text"
                tooltip = name + "TooltipText"
                if hasattr(widget, "setText") and text in ui_texts:
                    widget.setText(ui_texts[text])
                if hasattr(widget, "setToolTip") and tooltip in ui_texts:
                    widget.setToolTip(ui_texts[tooltip])
                    widget.setToolTipDuration(tooltip_duration)
            return True
        except Exception as e:
            ErrorHandler.handle_error(e, "ui", "warning")
            return False