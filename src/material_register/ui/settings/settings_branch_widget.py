from typing import TYPE_CHECKING

from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from material_register.controllers.settings_controllers.branch_settings_controller import (
    BranchSettingsController,
)
from material_register.services.error_handler import ErrorHandler
from material_register.ui.config.ui_constants import (
    LOG_LEVEL_WARNING,
    LOGGER_UI,
    UI_MARGINS_5,
    UI_SPACING,
)
from material_register.ui.setup.ui_settings import UiSettings
from material_register.ui.setup.ui_texts import UiTexts

if TYPE_CHECKING:
    from material_register.ui.dialogs.settings_dialog import SettingsDialog


class SettingsBranchWidget(QWidget):
    WIDTH = 400

    def __init__(self, settings_dialog: "SettingsDialog") -> None:
        super().__init__(settings_dialog)
        self.settings_dialog = settings_dialog
        self.branch_settings_controller = BranchSettingsController(self.settings_dialog)
        self.setLayout(self._create_ui())
        self._setup_ui()
        self._create_connection()

    def _create_ui(self) -> QVBoxLayout:
        main_layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        group_widget = QWidget()
        group_layout = QVBoxLayout()
        group_layout.setSpacing(UI_SPACING)
        group_layout.setContentsMargins(*UI_MARGINS_5)
        branch_group = self._create_branch_group()
        group_layout.addWidget(branch_group)
        group_layout.addStretch()
        actions_group = self._create_actions_group()
        group_widget.setLayout(group_layout)
        scroll_area.setWidget(group_widget)
        main_layout.addWidget(scroll_area, 1)
        main_layout.addWidget(actions_group, 0)
        return main_layout

    def _create_branch_group(self) -> QGroupBox:
        self.branch_group_box = QGroupBox()
        self.branch_group_box.setObjectName("branchGroupBox")
        main_layout = QVBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        container_layout = QHBoxLayout()
        container_layout.setSpacing(UI_SPACING)
        container_layout.setContentsMargins(*UI_MARGINS_5)
        form_layout = QFormLayout()
        form_layout.setSpacing(UI_SPACING)
        form_layout.setContentsMargins(*UI_MARGINS_5)
        self.company_name_label = QLabel()
        self.company_name_label.setObjectName("companyNameLabel")
        self.company_name_line_edit = QLineEdit()
        self.company_name_line_edit.setObjectName("companyNameLineEdit")
        self.branch_name_label = QLabel()
        self.branch_name_label.setObjectName("branchNameLabel")
        self.branch_name_line_edit = QLineEdit()
        self.branch_name_line_edit.setObjectName("branchNameLineEdit")
        self.branch_operator_label = QLabel()
        self.branch_operator_label.setObjectName("branchOperatorLabel")
        self.branch_operator_line_edit = QLineEdit()
        self.branch_operator_line_edit.setObjectName("branchOperatorLineEdit")
        self.branch_address_label = QLabel()
        self.branch_address_label.setObjectName("branchAddressLabel")
        self.branch_address_line_edit = QLineEdit()
        self.branch_address_line_edit.setObjectName("branchAddressLineEdit")
        self.phone_number_label = QLabel()
        self.phone_number_label.setObjectName("phoneNumberLabel")
        self.phone_number_line_edit = QLineEdit()
        self.phone_number_line_edit.setObjectName("phoneNumberLineEdit")
        self.email_address_label = QLabel()
        self.email_address_label.setObjectName("emailAddressLabel")
        self.email_address_line_edit = QLineEdit()
        self.email_address_line_edit.setObjectName("emailAddressLineEdit")
        self.company_id_label = QLabel()
        self.company_id_label.setObjectName("companyIdLabel")
        self.company_id_line_edit = QLineEdit()
        self.company_id_line_edit.setObjectName("companyIdLineEdit")
        self.tax_id_label = QLabel()
        self.tax_id_label.setObjectName("taxIdLabel")
        self.tax_id_line_edit = QLineEdit()
        self.tax_id_line_edit.setObjectName("taxIdLineEdit")
        self.establishment_id_label = QLabel()
        self.establishment_id_label.setObjectName("establishmentIdLabel")
        self.establishment_id_line_edit = QLineEdit()
        self.establishment_id_line_edit.setObjectName("establishmentIdLineEdit")
        self.facility_id_label = QLabel()
        self.facility_id_label.setObjectName("facilityIdLabel")
        self.facility_id_line_edit = QLineEdit()
        self.facility_id_line_edit.setObjectName("facilityIdLineEdit")
        self.opening_hours_label = QLabel()
        self.opening_hours_label.setObjectName("openingHoursLabel")
        self.opening_hours_line_edit = QLineEdit()
        self.opening_hours_line_edit.setObjectName("openingHoursLineEdit")
        form_layout.addRow(self.company_name_label, self.company_name_line_edit)
        form_layout.addRow(self.branch_name_label, self.branch_name_line_edit)
        form_layout.addRow(self.branch_operator_label, self.branch_operator_line_edit)
        form_layout.addRow(self.branch_address_label, self.branch_address_line_edit)
        form_layout.addRow(self.phone_number_label, self.phone_number_line_edit)
        form_layout.addRow(self.email_address_label, self.email_address_line_edit)
        form_layout.addRow(self.company_id_label, self.company_id_line_edit)
        form_layout.addRow(self.tax_id_label, self.tax_id_line_edit)
        form_layout.addRow(self.establishment_id_label, self.establishment_id_line_edit)
        form_layout.addRow(self.facility_id_label, self.facility_id_line_edit)
        form_layout.addRow(self.opening_hours_label, self.opening_hours_line_edit)
        container_layout.addLayout(form_layout)
        container_layout.addStretch()
        main_layout.addLayout(container_layout)
        self.branch_group_box.setLayout(main_layout)
        return self.branch_group_box

    def _create_actions_group(self) -> QGroupBox:
        self.actions_group_box = QGroupBox()
        self.actions_group_box.setObjectName("actionsGroupBox")
        main_layout = QHBoxLayout()
        main_layout.setSpacing(UI_SPACING)
        main_layout.setContentsMargins(*UI_MARGINS_5)
        self.settings_info_label = QLabel()
        self.settings_info_label.setObjectName("settingsInfoLabel")
        self.save_button = QPushButton()
        self.save_button.setObjectName("saveButton")
        main_layout.addWidget(self.settings_info_label)
        main_layout.addStretch()
        main_layout.addWidget(self.save_button)
        self.actions_group_box.setLayout(main_layout)
        return self.actions_group_box

    def _setup_ui(self) -> None:
        self._setup_texts()
        self._setup_edits()
        self._apply_settings()
        self._set_validators()

    def _setup_texts(self) -> None:
        widgets = self.findChildren(QWidget)
        if UiTexts.set_ui_texts(self, widgets):
            return
        ErrorHandler.handle_error(
            f"Texts load failed: {self.__class__.__name__}",
            LOGGER_UI,
            LOG_LEVEL_WARNING,
        )
        ErrorHandler.ui_texts_error = "TEXTS_LOAD_FAILED"
        UiTexts.set_default_texts(self, widgets)

    def _apply_settings(self) -> None:
        branch_settings = UiSettings.get_branch_settings()
        self.company_name_line_edit.setText(branch_settings.company_name or "")
        self.branch_name_line_edit.setText(branch_settings.branch_name or "")
        self.branch_operator_line_edit.setText(branch_settings.branch_operator or "")
        self.branch_address_line_edit.setText(branch_settings.branch_address or "")
        self.phone_number_line_edit.setText(branch_settings.phone_number or "")
        self.email_address_line_edit.setText(branch_settings.email_address or "")
        self.company_id_line_edit.setText(branch_settings.company_id or "")
        self.tax_id_line_edit.setText(branch_settings.tax_id or "")
        self.establishment_id_line_edit.setText(branch_settings.establishment_id or "")
        self.facility_id_line_edit.setText(branch_settings.facility_id or "")
        self.opening_hours_line_edit.setText(branch_settings.opening_hours or "")

    def _setup_edits(self) -> None:
        for edit in self.findChildren(QLineEdit):
            edit.setMinimumWidth(self.WIDTH)
            edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def _create_connection(self) -> None:
        self.save_button.clicked.connect(
            lambda: self.branch_settings_controller.update_branch_settings(self)
        )

    def _set_validators(self) -> None:
        company_validator = QRegularExpressionValidator(
            QRegularExpression(r"[\p{L}0-9 .,&\-]{1,30}")
        )
        person_name_validator = QRegularExpressionValidator(
            QRegularExpression(r"[\p{L}'\- ]{1,30}")
        )
        address_validator = QRegularExpressionValidator(
            QRegularExpression(r"[\p{L}0-9 .,:&'()\-\/]{1,50}")
        )
        phone_validator = QRegularExpressionValidator(
            QRegularExpression(r"[0-9+()\- ]{1,20}")
        )
        email_validator = QRegularExpressionValidator(
            QRegularExpression(r"[A-Za-z0-9._%+\-@]{1,50}")
        )
        identifier_validator = QRegularExpressionValidator(
            QRegularExpression(r"[\p{L}0-9 .\-\/]{1,30}")
        )
        opening_hours_validator = QRegularExpressionValidator(
            QRegularExpression(r"[\p{L}0-9 .,:;+\-\/()–]{1,50}")
        )
        self.company_name_line_edit.setValidator(company_validator)
        self.branch_name_line_edit.setValidator(company_validator)
        self.branch_operator_line_edit.setValidator(person_name_validator)
        self.branch_address_line_edit.setValidator(address_validator)
        self.phone_number_line_edit.setValidator(phone_validator)
        self.email_address_line_edit.setValidator(email_validator)
        self.opening_hours_line_edit.setValidator(opening_hours_validator)
        self.company_id_line_edit.setValidator(identifier_validator)
        self.tax_id_line_edit.setValidator(identifier_validator)
        self.establishment_id_line_edit.setValidator(identifier_validator)
        self.facility_id_line_edit.setValidator(identifier_validator)

    def branch_settings_data(self) -> dict[str, str]:
        return_data = {}
        for edit in self.findChildren(QLineEdit):
            key = edit.objectName().removesuffix("LineEdit")
            return_data[key] = edit.text().strip()
        return return_data
