NORMALIZED_COLUMNS = ["company_normalized", "first_name_normalized", "last_name_normalized", "document_number",
                      "address_normalized"]

IN_MODEL_COLUMNS = ["category", "commodity", "commodityId", "unitCount", "pricePerUnit", "totalPrice"]

OUT_MODEL_COLUMNS = ["category", "commodity", "commodityId", "unitCount"]

CUSTOMERS_HIDDEN_COLUMNS = ["id", "first_name", "last_name", "notes", "created_at", "company_normalized",
                      "first_name_normalized", "last_name_normalized", "address_normalized"]
CUSTOMERS_HORIZONTAL_PADDING = 50

TRANSFER_IN = "IN"
TRANSFER_OUT = "OUT"