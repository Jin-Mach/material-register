from pathlib import Path

REQUIRED_JSON_FILES = [
    Path("cs_CZ") / "ui_texts.json",
    Path("en_GB") / "ui_texts.json",
    Path("cs_CZ") / "error_texts.json",
    Path("en_GB") / "error_texts.json",
    Path("cs_CZ") / "headers_texts.json",
    Path("en_GB") / "headers_texts.json",
    Path("cs_CZ") / "confirm_texts.json",
    Path("en_GB") / "confirm_texts.json",
    Path("cs_CZ") / "notification_texts.json",
    Path("en_GB") / "notification_texts.json"
]

REQUIRED_IMAGES = [
    Path("system") / "SplashScreen.jpg",
    Path("customers") / "activeIcon.png",
    Path("customers") / "inactiveIcon.png",
]

UI_KEYS = [
    ("MainWindow", "titleText"),
    ("SidePanel", "transactionsButtonText"),
    ("SidePanel", "transactionsButtonTooltipText"),
    ("SidePanel", "customersButtonText"),
    ("SidePanel", "customersButtonTooltipText"),
    ("SidePanel", "catalogButtonText"),
    ("SidePanel", "catalogButtonTooltipText"),
    ("TransactionsActionsWidget", "addTransactionButtonTooltipText"),
    ("TransactionsActionsWidget", "deleteTransactionButtonTooltipText"),
    ("CustomersActionsWidget", "addCustomerButtonTooltipText"),
    ("CustomersActionsWidget", "searchLineEditPlaceholderText"),
    ("CustomersWidget", "countLabelText"),
    ("CustomersView", "updateCustomerActionText"),
    ("CustomersView", "activeCustomerActionText"),
    ("ErrorDialog", "closeDialogButtonText"),
    ("ErrorDialog", "closeDialogButtonTooltipText"),
    ("ErrorDialog", "closeAppButtonText"),
    ("ErrorDialog", "closeAppButtonTooltipText"),
    ("CustomerDialog", "titleText"),
    ("CustomerDialog", "createdLabelText"),
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
    ("CategoryDialog", "titleText"),
    ("CategoryDialog", "categoryNameLabelText"),
    ("CategoryDialog", "notesLabelText"),
    ("CategoryDialog", "notesCountLabelText"),
    ("CategoryDialog", "saveButtonText"),
    ("CategoryDialog", "saveButtonTooltipText"),
    ("CategoryDialog", "closeButtonText"),
    ("CategoryDialog", "closeButtonTooltipText"),
    ("CommodityDialog", "titleText"),
    ("CommodityDialog", "categoryLabelText"),
    ("CommodityDialog", "nameLabelText"),
    ("CommodityDialog", "unitLabelText"),
    ("CommodityDialog", "defaultPriceLabelText"),
    ("CommodityDialog", "activeLabelText"),
    ("CommodityDialog", "notesLabelText"),
    ("CommodityDialog", "notesCountLabelText"),
    ("CommodityDialog", "saveButtonText"),
    ("CommodityDialog", "saveButtonTooltipText"),
    ("CommodityDialog", "closeButtonText"),
    ("CommodityDialog", "closeButtonTooltipText"),
]

HEADERS_KEYS = [
    ("CustomersView", "company"),
    ("CustomersView", "document_number"),
    ("CustomersView", "address"),
]

ERROR_KEYS = [
    "APP_INIT_FAILED",
    "RESOURCES_MISSING",
    "DOWNLOAD_FAILED",
    "TEXTS_LOAD_FAILED",
    "CRITICAL_FAILURE",
    "UNKNOWN_ERROR",
]

CONFIRM_STRUCTURE = {
    "ACTIVE": ["TITLE", "TEXT", "YES", "NO"],
    "CUSTOMER_NOT_FOUND": ["TITLE", "TEXT", "CLOSE"],
}

NOTIFICATION_KEYS = [
    ("CUSTOMERS", "ADD_CUSTOMER"),
    ("CUSTOMERS", "UPDATE_CUSTOMER"),
    ("CUSTOMERS", "CHANGE_ACTIVE"),
    ("CATALOG", "ADD_CATEGORY"),
    ("CATALOG", "UPDATE_CATEGORY"),
    ("CATALOG", "ADD_COMMODITY"),
    ("CATALOG", "UPDATE_COMMODITY"),
]