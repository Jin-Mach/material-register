TRANSACTIONS_QUERY_IN = """
            SELECT
                    trans.id AS transaction_id,
                    trans.type AS transaction_type,
                    trans.created_at AS transaction_created_at,
                    trans.payment_type AS transaction_payment_type,
                
                    cust.id AS customer_id,
                    cust.document_number AS customer_document_number,
                    cust.address AS customer_address,
                    cust.company_normalized AS company_normalized,
                    cust.first_name_normalized AS first_name_normalized,
                    cust.last_name_normalized AS last_name_normalized,
                    cust.address_normalized AS address_normalized,
                
                    CASE
                        WHEN cust.company IS NOT NULL AND cust.company != ''
                            THEN cust.company
                        ELSE TRIM(cust.first_name || ' ' || cust.last_name)
                    END AS customer_name,
                
                    ROUND(SUM(items.unit_count * items.price_per_unit), 1) AS total
                
                FROM transactions trans
                LEFT JOIN customers cust ON cust.id = trans.customer_id
                LEFT JOIN transaction_items items ON items.transaction_id = trans.id
                
                WHERE 
                    trans.type = 'IN' 
                    AND trans.created_at >= date('now') 
                    AND trans.created_at < date('now', '+1 day')
                
                GROUP BY trans.id
                ORDER BY trans.id ASC
            """

TRANSACTIONS_QUERY_OUT = """
            SELECT
                    trans.id AS transaction_id,
                    trans.type AS transaction_type,
                    trans.created_at AS transaction_created_at,
                    trans.payment_type AS transaction_payment_type,
                
                    cust.id AS customer_id,
                    cust.document_number AS customer_document_number,
                    cust.address AS customer_address,
                    cust.company_normalized AS company_normalized,
                    cust.first_name_normalized AS first_name_normalized,
                    cust.last_name_normalized AS last_name_normalized,
                    cust.address_normalized AS address_normalized,
                
                    CASE
                        WHEN cust.company IS NOT NULL AND cust.company != ''
                            THEN cust.company
                        ELSE TRIM(cust.first_name || ' ' || cust.last_name)
                    END AS customer_name,
                
                    ROUND(SUM(items.unit_count), 1) AS total,
                    
                    con.unit AS suffix
                
                FROM transactions trans
                LEFT JOIN customers cust ON cust.id = trans.customer_id
                LEFT JOIN transaction_items items ON items.transaction_id = trans.id
                LEFT JOIN commodities con ON con.id = items.commodity_id  
                              
                WHERE 
                    trans.type = 'OUT' 
                    AND trans.created_at >= date('now') 
                    AND trans.created_at < date('now', '+1 day')
                
                GROUP BY trans.id
                ORDER BY trans.id ASC
            """

TRANSACTIONS_BASIC_FILTER_QUERY = """
            SELECT
                    trans.id AS transaction_id,
                    trans.type AS transaction_type,
                    trans.created_at AS transaction_created_at,
                    trans.payment_type AS transaction_payment_type,
                
                    cust.id AS customer_id,
                    cust.document_number AS customer_document_number,
                    cust.address AS customer_address,
                    cust.company_normalized AS company_normalized,
                    cust.first_name_normalized AS first_name_normalized,
                    cust.last_name_normalized AS last_name_normalized,
                    cust.address_normalized AS address_normalized,
                
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
                
                WHERE 
                    trans.type = ?
                    AND trans.created_at BETWEEN ? AND ?

                GROUP BY trans.id
                ORDER BY trans.id ASC;
            """