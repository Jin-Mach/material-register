NORMALIZED_COLUMNS = ["company_normalized", "first_name_normalized", "last_name_normalized", "document_number",
                      "address_normalized"]

IN_MODEL_COLUMNS = ["category", "commodity", "commodityId", "unitCount", "pricePerUnit", "totalPrice"]

OUT_MODEL_COLUMNS = ["category", "commodity", "commodityId", "unitCount"]

CUSTOMERS_HIDDEN_COLUMNS = ["id", "first_name", "last_name", "notes", "created_at", "company_normalized",
                      "first_name_normalized", "last_name_normalized", "address_normalized"]
CUSTOMERS_HORIZONTAL_PADDING = 50

ADD_MODE = "ADD"
UPDATE_MODE = "UPDATE"

TRANSFER_IN = "IN"
TRANSFER_OUT = "OUT"

TRANSACTION_INFO_WIDGET_NOTES_LENGTH = 200

TRANSACTION_VIEW_HIDDEN_COLUMNS = ["commodityId"]

CATEGORY_COMMODITY_DIALOG_MIN_VALUE = 0.0
CATEGORY_COMMODITY_DIALOG_MAX_UNIT_VALUE = 99_999_999.9
CATEGORY_COMMODITY_DIALOG_MAX_PRICE_VALUE = 1000.0

CATEGORY_DIALOG_NOTES_LENGTH = 100

COMMODITY_DIALOG_MIN_VALUE = 0.0
COMMODITY_DIALOG_MAX_PRICE_VALUE = 1000.0
COMMODITY_DIALOG_NOTES_LENGTH = 50

CREATE_TRANSACTION_DIALOG_PAYMENT_VALUES = ["CASH", "TRANSFER"]

CUSTOMERS_DIALOG_NOTES_LENGTH = 200
CUSTOMERS_DIALOG_INDIVIDUAL_INDEX = 0
CUSTOMERS_DIALOG_COMPANY_INDEX = 1