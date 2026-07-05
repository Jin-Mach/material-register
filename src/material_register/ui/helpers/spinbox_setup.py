from PySide6.QtWidgets import QDoubleSpinBox

from material_register.config.ui_constants import INTEGER_SUFFIXES


def set_suffix_mode(spinbox: QDoubleSpinBox, suffix: str) -> None:
    if suffix in INTEGER_SUFFIXES:
        spinbox.setDecimals(0)
        spinbox.setSingleStep(1)
        spinbox.setValue(round(spinbox.value()))
    else:
        spinbox.setDecimals(1)
        spinbox.setSingleStep(0.1)