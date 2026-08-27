TRANSACTIONS_QUERY_IN = """
            SELECT
                    trans.id AS transaction_id,
                    trans.type AS transaction_type,
                    trans.created_at AS transaction_created_at,
                    trans.payment_type AS transaction_payment_type,
                    trans.notes AS transaction_notes,
                
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
                    trans.notes AS transaction_notes,
                
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
                    trans.notes AS transaction_notes,
                
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

SELECTED_TRANSACTION_DATA = """
            SELECT
                trans_items.commodity_id AS commodity_id,
                trans_items.unit_count AS unit_count,
                trans_items.price_per_unit AS price_per_unit,
            
                commodities.name AS commodity_name,
                commodities.unit AS commodity_unit,
            
                categories.name AS category_name
            
            FROM transaction_items trans_items
            
            JOIN commodities ON commodities.id = trans_items.commodity_id
            JOIN categories ON categories.id = commodities.category_id
            
            WHERE trans_items.transaction_id = ?
"""

TRANSACTION_TOTAL_PRICE = """
            SELECT
                SUM(transaction_items.unit_count * transaction_items.price_per_unit) AS total_price
            
            FROM transactions
            
            JOIN transaction_items
                ON transaction_items.transaction_id = transactions.id
            
            WHERE transactions.type = 'IN'
              AND transactions.created_at BETWEEN ? AND ?
"""

INVENTORY_QUERY = """
            SELECT 
                categories.name AS category_name,

                commodities.name AS commodity_name,
                commodities.unit AS commodity_unit,

                inventory.stock AS inventory_stock,
                
                commodities.active AS commodity_active 

            FROM inventory inventory
            
            JOIN commodities ON commodities.id = inventory.commodity_id 
            JOIN categories ON commodities.category_id = categories.id

            ORDER BY categories.name ASC
"""
