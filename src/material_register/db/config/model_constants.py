NORMALIZED_COLUMNS = ["company_normalized", "first_name_normalized", "last_name_normalized", "document_number",
                      "address_normalized"]

ITEM_MODEL_IN_COLUMNS = ["category", "commodity", "commodityId", "unitCount", "pricePerUnit", "totalPrice"]
ITEM_MODEL_IN_LIST_COLUMNS = ["category", "commodity", "commodityId", "unitCount", "pricePerUnit"]
ITEM_MODEL_IN_COLUMNS_MAP = {"category": 0,
                        "commodity": 1,
                        "commodityId": 2,
                        "unitCount": 3,
                        "pricePerUnit": 4,
                        "totalPrice": 5
                             }

ITEM_MODEL_OUT_COLUMNS = ["category", "commodity", "commodityId", "unitCount"]
ITEM_MODEL_OUT_COLUMNS_MAP = {"category": 0,
                        "commodity": 1,
                        "commodityId": 2,
                        "unitCount": 3
                              }

LOAD_MODEL_IN_COLUMNS = ["transaction_created_at", "customer_name", "customer_document_number", "customer_address",
                         "total"]

CUSTOMERS_HIDDEN_COLUMNS = ["id", "first_name", "last_name", "notes", "created_at", "company_normalized",
                      "first_name_normalized", "last_name_normalized", "address_normalized"]

TRANSACTION_VIEW_HIDDEN_COLUMNS = ["commodityId"]

INVENTORY_COLUMNS = ["category", "commodity", "inventory_stock"]
INVENTORY_COLUMNS_MAP = {"category_name": 0,
                         "commodity_name": 1,
                         "commodity_unit": 2,
                         "inventory_stock": 3}

INVENTORY_VIEW_HIDDEN_COLUMNS = ["commodity_unit"]