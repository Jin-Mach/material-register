import pytest

from PySide6.QtWidgets import QPushButton, QWidget
from material_register.ui.setup.ui_texts import UiTexts


@pytest.fixture(autouse=True)
def reset_ui_texts():
    UiTexts.UI_TEXTS = {}
    yield
    UiTexts.UI_TEXTS = {}

@pytest.mark.parametrize(
    "ui_texts, expected_bool",
    [
        ({"QWidget": {"titleText": "Main Title"}}, True),
        ({}, False),
    ],
    ids=["ui_texts True", "ui_texts False"],
)
def test_set_ui_texts_bool(qtbot, ui_texts, expected_bool):
    widget = QWidget()
    qtbot.addWidget(widget)
    UiTexts.setup_init(ui_texts)
    result = UiTexts.set_ui_texts(widget, [])
    assert result == expected_bool

@pytest.mark.parametrize(
    "ui_texts, expected",
    [
        ({"QWidget": {"titleText": "Main Title"}}, "Main Title"),
        ({"QWidget": {"titleTextFake": "Main Title"}}, ""),
    ],
    ids=["title text", "no title text"],
)
def test_set_ui_texts_set_title(qtbot, ui_texts, expected):
    widget = QWidget()
    qtbot.addWidget(widget)
    UiTexts.setup_init(ui_texts)
    UiTexts.set_ui_texts(widget, [])
    assert widget.windowTitle() == expected

@pytest.mark.parametrize(
    "ui_texts, expected",
    [
        ({"QWidget": {"buttonText": "Button Text"}}, "Button Text"),
        ({"QWidget": {"buttonTextFake": "Button Text"}}, ""),
    ],
    ids=["button text", "no button text"],
)
def test_set_ui_texts_set_text(qtbot, ui_texts, expected):
    widget = QWidget()
    button = QPushButton()
    button.setObjectName("button")
    qtbot.addWidget(widget)
    qtbot.addWidget(button)
    UiTexts.setup_init(ui_texts)
    UiTexts.set_ui_texts(widget, [button])
    assert button.text() == expected

@pytest.mark.parametrize(
    "ui_texts, expected_tooltip, expected_duration",
    [
        ({"QWidget": {"buttonTooltipText": "Button Tooltip"}}, "Button Tooltip", 5000),
        ({"QWidget": {"buttonTooltipText": "Button Tooltip"}}, "Button Tooltip", 3000),
        ({"QWidget": {"buttonTooltipTextFake": "Button Tooltip"}}, "", 5000),
    ],
    ids=["default tooltip duration", "custom tooltip duration", "no tooltip"],
)
def test_set_ui_texts_set_tooltip(qtbot, ui_texts, expected_tooltip, expected_duration):
    widget = QWidget()
    button = QPushButton()
    button.setObjectName("button")
    qtbot.addWidget(widget)
    qtbot.addWidget(button)
    UiTexts.setup_init(ui_texts)
    UiTexts.set_ui_texts(widget, [button], tooltip_duration=expected_duration)
    assert button.toolTip() == expected_tooltip