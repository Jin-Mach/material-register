NORMALIZED_COLUMNS = ["company_normalized", "first_name_normalized", "last_name_normalized", "document_number",
                      "address_normalized"]

IN_MODEL_COLUMNS = ["category", "commodity", "commodityId", "unitCount", "pricePerUnit", "totalPrice"]
IN_MODEL_ITEMS_LIST_COLUMNS = ["category", "commodity", "commodityId", "unitCount", "pricePerUnit"]
IN_MODEL_COLUMNS_MAP = {"category": 0,
                        "commodity": 1,
                        "commodityId": 2,
                        "unitCount": 3,
                        "pricePerUnit": 4,
                        "totalPrice": 5
                        }

OUT_MODEL_COLUMNS = ["category", "commodity", "commodityId", "unitCount"]
OUT_MODEL_COLUMNS_MAP = {"category": 0,
                        "commodity": 1,
                        "commodityId": 2,
                        "unitCount": 3
                         }

CUSTOMERS_HIDDEN_COLUMNS = ["id", "first_name", "last_name", "notes", "created_at", "company_normalized",
                      "first_name_normalized", "last_name_normalized", "address_normalized"]

TRANSACTION_VIEW_HIDDEN_COLUMNS = ["commodityId"]