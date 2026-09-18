from typing import Any

from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QLineEdit,
    QRadioButton,
    QSpinBox,
    QWidget,
)

from material_register.domain.branch_dataclass import BranchDataclass


class UiSettings:
    SETTINGS = {}

    @classmethod
    def setup_init(cls, settings: dict[str, Any]) -> None:
        cls.SETTINGS = settings

    @classmethod
    def apply_settings(
        cls,
        main_key: str,
        sub_key: str,
        widgets: list[QWidget],
        settings_key: str = "user",
    ) -> bool:
        settings = cls.SETTINGS.get(main_key, {}).get(sub_key, {}).get(settings_key, {})
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

    @classmethod
    def get_branch_settings(cls) -> BranchDataclass:
        settings = cls.SETTINGS.get("branch", {})
        return BranchDataclass(
            company_name=settings.get("companyName"),
            branch_name=settings.get("branchName"),
            branch_operator=settings.get("branchOperator"),
            branch_address=settings.get("branchAddress"),
            phone_number=settings.get("phoneNumber"),
            email_address=settings.get("emailAddress"),
            company_id=settings.get("companyId"),
            tax_id=settings.get("taxId"),
            establishment_id=settings.get("establishmentId"),
            facility_id=settings.get("facilityId"),
            opening_hours=settings.get("openingHours"),
        )
