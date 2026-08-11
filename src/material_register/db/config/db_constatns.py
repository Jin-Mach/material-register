DATABASE_NAME = "material_register"

DATABASE_SCHEMA = {
    "customers": {
        "id",
        "company",
        "first_name",
        "last_name",
        "document_number",
        "address",
        "notes",
        "created_at",
        "active",
        "company_normalized",
        "first_name_normalized",
        "last_name_normalized",
        "address_normalized",
    },
    "categories": {
        "id",
        "name",
        "notes",
    },
    "commodities": {
        "id",
        "name",
        "category_id",
        "unit",
        "default_price",
        "notes",
        "active",
    },
    "inventory": {
        "commodity_id",
        "stock",
    },
    "transactions": {
        "id",
        "type",
        "customer_id",
        "created_at",
        "payment_type",
        "notes",
    },
    "transaction_items": {
        "id",
        "transaction_id",
        "commodity_id",
        "unit_count",
        "price_per_unit",
    },
}
