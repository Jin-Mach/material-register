ADVANCED_SEARCH_COLUMNS = {
    "transaction_id": "trans.id",
    "transaction_type": "trans.type",
    "transaction_created_at": "trans.created_at",
    "transaction_payment_type": "trans.payment_type",
    "transaction_is_invoiced": "trans.is_invoiced",
    "transaction_notes": "trans.notes",
    "total": "total",
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
                        ), 1) AS total,

                    CASE
                        WHEN trans.type = 'OUT' THEN con.unit
                        ELSE NULL
                    END AS suffix

                FROM transactions trans

                LEFT JOIN customers cust ON cust.id = trans.customer_id
                LEFT JOIN transaction_items items ON items.transaction_id = trans.id
                LEFT JOIN commodities con ON con.id = items.commodity_id
                LEFT JOIN categories cat ON cat.id = con.category_id
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
                ), 1) AS transactions_amount

            FROM transactions trans

            LEFT JOIN customers cust ON cust.id = trans.customer_id
            LEFT JOIN transaction_items items ON items.transaction_id = trans.id
            LEFT JOIN commodities con ON con.id = items.commodity_id
            LEFT JOIN categories cat ON cat.id = con.category_id

            WHERE trans.id IN (
                SELECT trans.id
            
                FROM transactions trans
            
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
