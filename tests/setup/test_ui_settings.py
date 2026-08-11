from PySide6.QtWidgets import QCheckBox, QLineEdit, QRadioButton, QSpinBox, QWidget

from material_register.ui.setup.ui_settings import UiSettings


def test_set_ui_settings_line_edit(qtbot):
    widget = QWidget()
    line_edit = QLineEdit()
    line_edit.setObjectName("branchNameLineEdit")
    qtbot.addWidget(widget)
    qtbot.addWidget(line_edit)
    UiSettings.setup_init({
        "export": {
            "user": {
                "branchNameLineEdit": "Some branch"
            }
        }
    })
    result = UiSettings().set_ui_settings("export", [line_edit])
    assert result is True
    assert line_edit.text() == "Some branch"

def test_set_ui_settings_spinbox(qtbot):
    widget = QWidget()
    spinbox = QSpinBox()
    spinbox.setObjectName("openingBalanceSpinbox")
    spinbox.setRange(0, 10000)
    qtbot.addWidget(widget)
    qtbot.addWidget(spinbox)
    UiSettings.setup_init({
        "export": {
            "user": {
                "openingBalanceSpinbox": 1000
            }
        }
    })
    result = UiSettings().set_ui_settings("export", [spinbox])
    assert result is True
    assert spinbox.value() == 1000

def test_set_ui_settings_checkbox(qtbot):
    widget = QWidget()
    checkbox = QCheckBox()
    checkbox.setObjectName("saveLastBalanceCheckbox")
    qtbot.addWidget(widget)
    qtbot.addWidget(checkbox)
    UiSettings.setup_init({
        "export": {
            "user": {
                "saveLastBalanceCheckbox": True
            }
        }
    })
    result = UiSettings().set_ui_settings("export", [checkbox])
    assert result is True
    assert checkbox.isChecked() is True

def test_set_ui_settings_radiobutton(qtbot):
    widget = QWidget()
    radio = QRadioButton()
    radio.setObjectName("openFolderRadioButton")
    qtbot.addWidget(widget)
    qtbot.addWidget(radio)
    UiSettings.setup_init({
        "export": {
            "user": {
                "openFolderRadioButton": True
            }
        }
    })
    result = UiSettings().set_ui_settings("export", [radio])
    assert result is True
    assert radio.isChecked() is True

def test_set_ui_settings_multiple_widgets(qtbot):
    widget = QWidget()
    branch = QLineEdit()
    branch.setObjectName("branchNameLineEdit")
    save_checkbox = QCheckBox()
    save_checkbox.setObjectName("saveLastBalanceCheckbox")
    qtbot.addWidget(widget)
    qtbot.addWidget(branch)
    qtbot.addWidget(save_checkbox)
    UiSettings.setup_init({
        "export": {
            "user": {
                "branchNameLineEdit": "Warehouse",
                "saveLastBalanceCheckbox": False
            }
        }
    })
    result = UiSettings().set_ui_settings(
        "export",
        [branch, save_checkbox]
    )
    assert result is True
    assert branch.text() == "Warehouse"
    assert save_checkbox.isChecked() is False

def test_set_ui_settings_missing_data(qtbot):
    widget = QWidget()
    line_edit = QLineEdit()
    line_edit.setObjectName("branchNameLineEdit")
    qtbot.addWidget(widget)
    qtbot.addWidget(line_edit)
    UiSettings.setup_init({})
    result = UiSettings().set_ui_settings("export", [line_edit])
    assert result is False
    assert line_edit.text() == ""

def test_set_ui_settings_missing_key(qtbot):
    widget = QWidget()
    line_edit = QLineEdit()
    line_edit.setObjectName("branchNameLineEdit")
    qtbot.addWidget(widget)
    qtbot.addWidget(line_edit)
    UiSettings.setup_init({
        "export": {
            "user": {
                "otherSetting": "X"
            }
        }
    })
    result = UiSettings().set_ui_settings("export", [line_edit])
    assert result is True
    assert line_edit.text() == ""