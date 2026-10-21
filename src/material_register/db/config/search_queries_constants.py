SEARCH_QUERY_START = """
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
"""

SEARCH_QUERY_END = """
            GROUP BY trans.id
            ORDER BY trans.created_at DESC, trans.id DESC;
"""

SEARCH_TRANSACTIONS_AMOUNT_QUERY_START = """
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
            
            LEFT JOIN transaction_items items ON items.transaction_id = trans.id
            LEFT JOIN customers cust ON cust.id = trans.customer_id
"""

MATERIAL_QUERY_START = """
            SELECT
                categories.name AS category_name,
                commodities.name AS commodity_name,
                commodities.unit AS commodity_unit,

                SUM(
                    CASE
                        WHEN trans.type = 'IN'
                            THEN transaction_items.unit_count
                        WHEN trans.type = 'OUT'
                            THEN -transaction_items.unit_count
                    END
                ) AS total

            FROM transaction_items

            LEFT JOIN transactions AS trans
                ON trans.id = transaction_items.transaction_id
            LEFT JOIN customers
                ON customers.id = trans.customer_id
            LEFT JOIN commodities
                ON commodities.id = transaction_items.commodity_id
            LEFT JOIN categories
                ON categories.id = commodities.category_id
"""

MATERIAL_QUERY_END = """
            GROUP BY
                commodities.id,
                categories.name,
                commodities.name,
                commodities.unit
            ORDER BY
                categories.name ASC,
                commodities.name ASC;
"""

SEARCH_PERIOD_QUERY = "trans.created_at BETWEEN ? AND ?"

SEARCH_VALUE_QUERY = """
            (
                document_number LIKE ?
                OR company_normalized LIKE ?
                OR first_name_normalized LIKE ?
                OR last_name_normalized LIKE ?
                OR address_normalized LIKE ?
            )
"""
