ADVANCED_SEARCH_COLUMNS = {
    "transaction_id": "trans.id",
    "transaction_type": "trans.type",
    "transaction_created_at": "trans.created_at",
    "transaction_payment_type": "trans.payment_type",
    "transaction_is_invoiced": "trans.is_invoiced",
    "transaction_notes": "trans.notes",
    "total": "total",
    "customer_subject_type": "cust.company",
    "customer_company_name": "cust.company_normalized",
    "customer_first_name": "cust.first_name_normalized",
    "customer_last_name": "cust.last_name_normalized",
    "customer_document": "cust.document_number",
    "customer_address": "cust.address_normalized",
    "customer_active": "cust.active",
    "customer_notes": "cust.notes",
}

WHERE_CLAUSE = "WHERE"
HAVING_CLAUSE = "HAVING"


ADVANCED_SEARCH_QUERY_START = """
    SELECT
        trans.id AS transaction_id,
        trans.type AS transaction_type,
        trans.created_at AS transaction_created_at,
        trans.payment_type AS transaction_payment_type,
        trans.is_invoiced AS transaction_is_invoiced,
        trans.notes AS transaction_notes,

        cust.id AS customer_id,
        cust.document_number AS customer_document_number,
        cust.address AS customer_address,

        CASE
            WHEN cust.company IS NOT NULL AND cust.company != ''
                THEN cust.company
            ELSE TRIM(cust.first_name || ' ' || cust.last_name)
        END AS customer_name,

        ROUND(
            SUM(
                CASE
                    WHEN trans.type = 'IN'
                        THEN items.unit_count * items.price_per_unit
                    ELSE items.unit_count
                END
            ), 1
        ) AS total,

        CASE
            WHEN trans.type = 'OUT' THEN con.unit
            ELSE NULL
        END AS suffix

    FROM transactions trans

    LEFT JOIN customers cust
        ON cust.id = trans.customer_id
    LEFT JOIN transaction_items items
        ON items.transaction_id = trans.id
    LEFT JOIN commodities con
        ON con.id = items.commodity_id
    LEFT JOIN categories cat
        ON cat.id = con.category_id
"""

ADVANCED_SEARCH_QUERY_GROUP_BY = "GROUP BY trans.id"

ADVANCED_SEARCH_QUERY_ORDER_BY = "ORDER BY trans.created_at DESC, trans.id DESC;"


ADVANCED_SEARCH_TRANSACTIONS_AMOUNT_QUERY_START = """
    SELECT
        ROUND(
            SUM(
                CASE
                    WHEN trans.type = 'IN'
                        THEN items.unit_count * items.price_per_unit
                    ELSE 0
                END
            ), 1
        ) AS transactions_amount

    FROM transactions trans

    LEFT JOIN customers cust
        ON cust.id = trans.customer_id
    LEFT JOIN transaction_items items
        ON items.transaction_id = trans.id
    LEFT JOIN commodities con
        ON con.id = items.commodity_id
    LEFT JOIN categories cat
        ON cat.id = con.category_id

    WHERE trans.id IN (
        SELECT trans.id

        FROM transactions trans

        LEFT JOIN customers cust
            ON cust.id = trans.customer_id
        LEFT JOIN transaction_items items
            ON items.transaction_id = trans.id
"""


ADVANCED_SEARCH_AMOUNT_EXPRESSION = """
    ROUND(
        SUM(
            CASE
                WHEN trans.type = 'IN'
                    THEN items.unit_count * items.price_per_unit
                ELSE items.unit_count
            END
        ), 1)
"""


ADVANCED_SEARCH_MATERIAL_QUERY_START = """
    SELECT
        categories.name AS category_name,
        commodities.name AS commodity_name,
        commodities.unit AS commodity_unit,

        ROUND(
            SUM(
                CASE
                    WHEN trans.type = 'IN'
                        THEN transaction_items.unit_count
                    WHEN trans.type = 'OUT'
                        THEN -transaction_items.unit_count
                END
            ), 1
        ) AS total

    FROM transaction_items

    LEFT JOIN transactions AS trans
        ON trans.id = transaction_items.transaction_id
    LEFT JOIN customers cust
        ON cust.id = trans.customer_id
    LEFT JOIN commodities
        ON commodities.id = transaction_items.commodity_id
    LEFT JOIN categories
        ON categories.id = commodities.category_id

    WHERE trans.id IN (
        SELECT trans.id

        FROM transactions trans

        LEFT JOIN customers cust
            ON cust.id = trans.customer_id
        LEFT JOIN transaction_items items
            ON items.transaction_id = trans.id
"""

MATERIAL_FILTER_EXISTS_START = """
    EXISTS (
        SELECT 1
        
        FROM transaction_items AS material_item
        
        JOIN commodities AS material_commodity
            ON material_commodity.id = material_item.commodity_id
        JOIN categories AS material_category
            ON material_category.id = material_commodity.category_id
        WHERE material_item.transaction_id = trans.id
"""

MATERIAL_FILTER_CATEGORY = "AND material_category.id = ?"

MATERIAL_FILTER_COMMODITY = "AND material_commodity.id = ?"

MATERIAL_FILTER_GROUP_BY = """
    GROUP BY material_item.transaction_id, material_commodity.id
"""

MATERIAL_FILTER_AMOUNT = "SUM(material_item.unit_count) {operator} ?"

MATERIAL_FILTER_TOTAL_PRICE = """
    SUM(material_item.unit_count * material_item.price_per_unit) {operator} ?
"""

MATERIAL_FILTER_PRICE_PER_UNIT = """
    EXISTS (
        SELECT 1
        
        FROM transaction_items AS price_item
        
        WHERE price_item.transaction_id = trans.id
          AND price_item.commodity_id = material_commodity.id
          AND price_item.price_per_unit {operator} ?
    )
"""

MATERIAL_FILTER_EXISTS_END = ")"

ADVANCED_SEARCH_MATERIAL_QUERY_GROUP_BY = """
    GROUP BY
        commodities.id,
        categories.name,
        commodities.name,
        commodities.unit
"""

ADVANCED_SEARCH_MATERIAL_QUERY_ORDER_BY = """
    ORDER BY
        categories.name ASC,
        commodities.name ASC;
"""
