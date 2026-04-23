import pytest

from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget
from material_register.ui.setup.texts_setup import TextsSetup


@pytest.mark.parametrize("ui_texts, expected_bool", [
    ({"QMainWindow": {"titleText": "Main Title"}}, True),
    ({}, False),
], ids=["ui_texts True", "ui_texts False"])
def test_set_ui_texts_bool(qtbot, ui_texts, expected_bool) -> None:
    window = QMainWindow()
    TextsSetup.setup_init(ui_texts)
    result = TextsSetup.set_ui_texts(window, [])
    assert result == expected_bool

@pytest.mark.parametrize("ui_texts, expected", [
    ({"QMainWindow": {"titleText": "Main Title"}}, "Main Title"),
    ({"QMainWindow": {"titleTextFake": "Main Title"}}, ""),
], ids=["title text", "no title text"])
def test_set_ui_texts_set_title(qtbot, ui_texts, expected) -> None:
    window = QMainWindow()
    TextsSetup.setup_init(ui_texts)
    TextsSetup.set_ui_texts(window, [])
    assert window.windowTitle() == expected

@pytest.mark.parametrize("ui_texts, expected", [
    ({"QWidget": {"buttonText": "Button Text"}}, "Button Text"),
    ({"QWidget": {"buttonTextFake": "Button Text"}}, ""),
], ids=["button text", "no button text"])
def test_set_ui_texts_set_text(qtbot, ui_texts, expected) -> None:
    widget = QWidget()
    button = QPushButton()
    button.setObjectName("button")
    TextsSetup.setup_init(ui_texts)
    TextsSetup.set_ui_texts(widget, [button])
    assert button.text() == expected