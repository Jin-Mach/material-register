import pytest

from PySide6.QtWidgets import QWidget, QPushButton
from material_register.ui.setup.ui_texts import UiTexts


@pytest.fixture(autouse=True)
def reset_ui_texts():
    UiTexts.UI_TEXTS = {}
    yield
    UiTexts.UI_TEXTS = {}

def test_set_ui_texts_button_text(qtbot):
    widget = QWidget()
    button = QPushButton()
    button.setObjectName("button")
    qtbot.addWidget(widget)
    qtbot.addWidget(button)
    UiTexts.setup_init({
        "QWidget": {
            "buttonText": "Button Text"
        }
    })
    result = UiTexts.set_ui_texts(widget, [button])
    assert result is True
    assert button.text() == "Button Text"

def test_set_ui_texts_tooltip(qtbot):
    widget = QWidget()
    button = QPushButton()
    button.setObjectName("button")
    qtbot.addWidget(widget)
    qtbot.addWidget(button)
    UiTexts.setup_init({
        "QWidget": {
            "buttonTooltipText": "Tooltip text"
        }
    })
    result = UiTexts.set_ui_texts(widget, [button], tooltip_duration=3000)
    assert result is True
    assert button.toolTip() == "Tooltip text"

def test_set_ui_texts_window_title(qtbot):
    widget = QWidget()
    qtbot.addWidget(widget)
    UiTexts.setup_init({
        "QWidget": {
            "titleText": "Main Title"
        }
    })
    result = UiTexts.set_ui_texts(widget, [])
    assert result is True
    assert widget.windowTitle() == "Main Title"

def test_set_ui_texts_no_data(qtbot):
    widget = QWidget()
    button = QPushButton()
    button.setObjectName("button")
    qtbot.addWidget(widget)
    qtbot.addWidget(button)
    UiTexts.setup_init({})
    result = UiTexts.set_ui_texts(widget, [button])
    assert result is False
    assert button.text() == ""

def test_set_ui_texts_missing_key(qtbot):
    widget = QWidget()
    button = QPushButton()
    button.setObjectName("button")
    qtbot.addWidget(widget)
    qtbot.addWidget(button)
    UiTexts.setup_init({
        "QWidget": {
            "otherText": "X"
        }
    })
    UiTexts.set_ui_texts(widget, [button])
    assert button.text() == ""