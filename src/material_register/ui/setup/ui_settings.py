from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QWidget,
)


class UiSettings:
    SETTINGS = {}

    @classmethod
    def setup_init(cls, settings: dict[str, Any]) -> None:
        cls.SETTINGS = settings

    @classmethod
    def set_ui_settings(cls, main_key: str, widgets: list[QWidget], sub_key: str = "user") -> bool:
        settings = cls.SETTINGS.get(main_key, {}).get(sub_key, {})
        if not settings:
            return False
        for widget in widgets:
            key = widget.objectName()
            if key in settings:
                if isinstance(widget, QLineEdit):
                    widget.setText(settings.get(key, ""))
                elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    widget.setValue(settings.get(key, 0.0))
                elif isinstance(widget, (QCheckBox, QRadioButton)):
                    widget.setChecked(settings.get(key, False))
        return True