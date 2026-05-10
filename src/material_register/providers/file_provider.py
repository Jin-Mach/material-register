import json

from pathlib import Path

from material_register.services.error_handler import ErrorHandler


class FileProvider:
    REQUIRED_JSON_FILES = [
        Path("cs_CZ") / "ui_texts.json",
        Path("en_GB") / "ui_texts.json",
        Path("cs_CZ") / "error_texts.json",
        Path("en_GB") / "error_texts.json",
        Path("cs_CZ") / "headers_texts.json",
        Path("en_GB") / "headers_texts.json",
    ]

    REQUIRED_IMAGES = [
        Path("SplashScreen.jpg"),
    ]

    UI_KEYS = [
        ("MainWindow", "titleText"),
        ("SidePanel", "transactionsButtonText"),
        ("SidePanel", "transactionsButtonTooltipText"),
        ("SidePanel", "customersButtonText"),
        ("SidePanel", "customersButtonTooltipText"),
        ("TransactionsActionsWidget", "addTransactionButtonTooltipText"),
        ("TransactionsActionsWidget", "deleteTransactionButtonTooltipText"),
        ("CustomersActionsWidget", "addCustomerButtonTooltipText"),
        ("CustomersActionsWidget", "updateCustomerButtonTooltipText"),
        ("CustomersActionsWidget", "activeCustomerButtonTooltipText"),
        ("CustomersView", "updateCustomerActionText"),
        ("CustomersView", "activeCustomerActionText"),
        ("ErrorDialog", "closeDialogButtonText"),
        ("ErrorDialog", "closeDialogButtonTooltipText"),
        ("ErrorDialog", "closeAppButtonText"),
        ("ErrorDialog", "closeAppButtonTooltipText"),
        ("CustomerDialog", "titleText"),
        ("CustomerDialog", "subjectTypePlaceholderText"),
        ("CustomerDialog", "subjectTypeItems"),
        ("CustomerDialog", "companyLabelText"),
        ("CustomerDialog", "firstNameLabelText"),
        ("CustomerDialog", "lastNameLabelText"),
        ("CustomerDialog", "documentTypeLabelText"),
        ("CustomerDialog", "addressLabelText"),
        ("CustomerDialog", "activeLabelText"),
        ("CustomerDialog", "notesLabelText"),
        ("CustomerDialog", "notesCountLabelText"),
        ("CustomerDialog", "saveButtonText"),
        ("CustomerDialog", "saveButtonTooltipText"),
        ("CustomerDialog", "closeButtonText"),
        ("CustomerDialog", "closeButtonTooltipText"),
    ]

    HEADERS_KEYS = [
        ("CustomersView", "company"),
        ("CustomersView", "document_number"),
        ("CustomersView", "address"),
        ("CustomersView", "active"),
    ]

    ERROR_KEYS = [
        "APP_INIT_FAILED",
        "RESOURCES_MISSING",
        "DOWNLOAD_FAILED",
        "TEXTS_LOAD_FAILED",
        "CRITICAL_FAILURE",
        "UNKNOWN_ERROR",
    ]

    @classmethod
    def check_missing_files(cls, resources_path: Path) -> set[Path]:
        invalid_files = set()
        texts_folder = cls._check_json_files(resources_path / "texts")
        invalid_files.update(texts_folder)
        images_folder = cls._check_images(resources_path / "images")
        invalid_files.update(images_folder)
        return invalid_files

    @classmethod
    def _check_json_files(cls, base_path: Path) -> set[Path]:
        invalid_files = set()
        for path in cls.REQUIRED_JSON_FILES:
            file_path = base_path / path
            if not file_path.exists():
                invalid_files.add(file_path)
                continue
            if not cls._is_file_valid(file_path):
                invalid_files.add(file_path)
        return invalid_files

    @classmethod
    def _check_images(cls, base_path: Path) -> set[Path]:
        invalid_files = set()
        for file in cls.REQUIRED_IMAGES:
            image_path = base_path / file
            if not image_path.exists():
                invalid_files.add(image_path)
        return invalid_files

    @classmethod
    def _is_file_valid(cls, file: Path) -> bool:
        try:
            name = file.stem
            data = json.loads(file.read_text(encoding="utf-8"))
            if name == "ui_texts":
                return cls._check_ui_json(data)
            if name == "error_texts":
                return cls._check_error_json(data)
            if name == "headers_texts":
                return cls._check_headers_json(data)
            return False
        except Exception as e:
            ErrorHandler.handle_error(e, "app", "error")
            return False

    @classmethod
    def _check_ui_json(cls, data: dict[str, dict[str, str]]) -> bool:
        for section, key in cls.UI_KEYS:
            if section not in data:
                return False
            if key not in data[section]:
                return False
            value = data[section][key]
            if value is None or value == "":
                return False
        return True

    @classmethod
    def _check_error_json(cls, data: dict[str, str]) -> bool:
        for key in cls.ERROR_KEYS:
            if key not in data:
                return False
            if not data[key]:
                return False
        return True

    @classmethod
    def _check_headers_json(cls, data: dict[str, dict[str, str]]) -> bool:
        for section, key in cls.HEADERS_KEYS:
            if section not in data:
                return False
            if key not in data[section]:
                return False
            value = data[section][key]
            if value is None or value == "":
                return False
        return True