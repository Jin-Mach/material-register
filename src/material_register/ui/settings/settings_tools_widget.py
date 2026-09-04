from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QScrollArea, QHBoxLayout, QPushButton, QCheckBox, QLabel

from material_register.services.error_handler import ErrorHandler
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class SettingsToolsWidget(QWidget):
    SPACING = 10

    def __init__(self, settings_dialog: "SettingsDialog"):
        super().__init__(settings_dialog)
        self.settings_dialog = settings_dialog
        self.setLayout(self._create_ui())
        self._setup_ui()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        group_widget = QWidget()
        group_layout = QVBoxLayout()
        group_layout.setSpacing(self.SPACING)
        tools_group = self._create_tools_group()
        cash_balance_group = self._create_cash_balance_group()
        group_layout.addWidget(tools_group)
        group_layout.addWidget(cash_balance_group)
        group_layout.addStretch()
        actions_group = self._create_actions_group()
        group_widget.setLayout(group_layout)
        scroll_area.setWidget(group_widget)
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(actions_group)
        return main_layout

    def _setup_ui(self) -> None:
        self._setup_texts()

    def _create_tools_group(self) -> QGroupBox:
        self.tools_group_box = QGroupBox()
        self.tools_group_box.setObjectName("toolsGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        self.container_size = QCheckBox()
        self.container_size.setObjectName("containerSizeCheckbox")
        main_layout.addWidget(self.container_size)
        self.tools_group_box.setLayout(main_layout)
        return self.tools_group_box

    def _create_cash_balance_group(self) -> QGroupBox:
        self.cash_balance_group_box = QGroupBox()
        self.cash_balance_group_box.setObjectName("cashBalanceGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self.SPACING)
        self.balance_cash = QCheckBox()
        self.balance_cash.setObjectName("balanceCashCheckbox")
        self.values_cash = QCheckBox()
        self.values_cash.setObjectName("valuesCashCheckbox")
        self.others_cash = QCheckBox()
        self.others_cash.setObjectName("othersCashCheckbox")
        main_layout.addWidget(self.balance_cash)
        main_layout.addWidget(self.values_cash)
        main_layout.addWidget(self.others_cash)
        self.cash_balance_group_box.setLayout(main_layout)
        return self.cash_balance_group_box

    def _create_actions_group(self) -> QGroupBox:
        self.actions_group_box = QGroupBox()
        self.actions_group_box.setObjectName("actionsGroupBox")
        main_layout = QHBoxLayout()
        main_layout.setSpacing(self.SPACING)
        self.settings_info_label = QLabel()
        self.settings_info_label.setObjectName("settingsInfoLabel")
        self.restore_button = QPushButton()
        self.restore_button.setObjectName("restoreButton")
        self.save_button = QPushButton()
        self.save_button.setObjectName("saveButton")
        main_layout.addWidget(self.settings_info_label)
        main_layout.addStretch()
        main_layout.addWidget(self.restore_button)
        main_layout.addWidget(self.save_button)
        self.actions_group_box.setLayout(main_layout)
        return self.actions_group_box

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        if not UiTexts.set_ui_texts(self, widgets):
            ErrorHandler.handle_error(f"Settings load failed: {self.__class__.__name__}", "ui", "warning")
            ErrorHandler.ui_texts_error = "CONFIG_LOAD_FAILED"
            return

    def get_tools_settings_data(self) -> dict[str, bool]:
        return {
            self.container_size.objectName(): self.container_size.isChecked(),
            self.balance_cash.objectName(): self.balance_cash.isChecked(),
            self.values_cash.objectName(): self.values_cash.isChecked(),
            self.others_cash.objectName(): self.others_cash.isChecked(),
        }
