from typing import Any

from PySide6.QtWidgets import QWidget, QLineEdit, QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton


class UiSettings:
    SETTINGS = {}

    @classmethod
    def setup_init(cls, settings: dict[str, Any]) -> None:
        cls.SETTINGS = settings

    def set_ui_settings(self, main_key: str, widgets: list[QWidget]) -> bool:
        settings = self.SETTINGS.get(main_key, {})
        if not settings:
            return False
        for widget in widgets:
            key = widget.objectName()
            if isinstance(widget, QLineEdit):
                widget.setText(settings.get(key, ""))
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                widget.setValue(settings.get(key, 0.0))
            elif isinstance(widget, (QCheckBox, QRadioButton)):
                widget.setChecked(settings.get(key, False))
        return True