SUMMARY_QUERY_IN = """
            SELECT
                category.name AS category,
                
                commodity.name AS commodity,
                commodity.unit AS commodity_unit,
                
                items.price_per_unit,
                
                ROUND(SUM(items.unit_count), 1) AS total_quantity,
                ROUND(SUM(items.unit_count * items.price_per_unit), 1) AS total_price
            
            FROM transactions trans
            
            JOIN transaction_items items
                ON items.transaction_id = trans.id
            
            JOIN commodities commodity
                ON commodity.id = items.commodity_id
            
            LEFT JOIN categories category
                ON category.id = commodity.category_id
            
            WHERE
                trans.type = 'IN'
                AND trans.payment_type = 'CASH'
                AND trans.created_at >= ?
                AND trans.created_at <= ?
            
            GROUP BY
                category.name,
                commodity.name,
                items.price_per_unit
            
            ORDER BY
                category.name,
                commodity.name,
                items.price_per_unit
"""
SUMMARY_QUERY_OUT = """
            SELECT
            
                category.name AS category,
                
                commodity.name AS commodity,
                commodity.unit AS commodity_unit,
                
                ROUND(SUM(items.unit_count), 1) AS total_quantity
                
            FROM transactions trans
            
            JOIN transaction_items items
                ON items.transaction_id = trans.id
            
            JOIN commodities commodity
                ON commodity.id = items.commodity_id
                
            LEFT JOIN categories category
                ON category.id = commodity.category_id
            
            WHERE trans.type = 'OUT'
                AND trans.created_at >= ?
                AND trans.created_at <= ?
            
            GROUP BY
                category.name,
                commodity.name,
                commodity.unit
            
            ORDER BY
                category.name,
                commodity.name
"""

TRANSACTIONS_QUERY_IN = """
            SELECT
                
                date(trans.created_at) AS transaction_date,
                trans.created_at AS created_at,
                trans.payment_type AS payment_type,

                customer.document_number AS document_number,
                customer.address AS address,
                
                trans_items.unit_count AS unit_count,
                trans_items.price_per_unit AS price_per_unit,
                
                commodity.name AS commodity_name,
                commodity.unit AS commodity_unit,
                
                category.name AS category,
                
            CASE
                WHEN customer.company IS NOT NULL AND customer.company != ''
                    THEN customer.company
                ELSE TRIM(customer.first_name || ' ' || customer.last_name)
            END AS customer_name
                            
            FROM transactions trans
            
            LEFT JOIN customers customer
                ON customer.id = trans.customer_id
                
            LEFT JOIN transaction_items trans_items
                ON trans_items.transaction_id = trans.id
                
            LEFT JOIN commodities commodity
                ON commodity.id = trans_items.commodity_id
                
            LEFT JOIN categories category
                ON category.id = commodity.category_id
            
            WHERE trans.type = 'IN'
                AND trans.created_at >= ?
                AND trans.created_at <= ?
                AND (? IS NULL OR customer.id = ?)
                
            ORDER BY
                transaction_date ASC,
                customer_name ASC,
                created_at ASC,
                category ASC,
                commodity_name ASC,
                price_per_unit ASC;
"""

TRANSACTIONS_QUERY_OUT = """
            SELECT
                
                date(trans.created_at) AS transaction_date,
                trans.created_at AS created_at,
                
                customer.document_number AS document_number,
                customer.address AS address,
                
                trans_items.unit_count AS unit_count,
                
                commodity.name AS commodity_name,
                commodity.unit AS commodity_unit,
                
                category.name AS category,
                
            CASE
                WHEN customer.company IS NOT NULL AND customer.company != ''
                    THEN customer.company
                ELSE TRIM(customer.first_name || ' ' || customer.last_name)
            END AS customer_name
            
            FROM transactions trans
            
            LEFT JOIN customers customer
                ON customer.id = trans.customer_id
                
            LEFT JOIN transaction_items trans_items
                ON trans_items.transaction_id = trans.id
                
            LEFT JOIN commodities commodity
                ON commodity.id = trans_items.commodity_id
            
            LEFT JOIN categories category
                ON category.id = commodity.category_id
                
            WHERE trans.type = 'OUT'
                AND trans.created_at >= ?
                AND trans.created_at <= ?
                AND (? IS NULL OR customer.id = ?)
                
            ORDER BY
                transaction_date ASC,
                customer_name ASC,
                created_at ASC,
                category ASC,
                commodity_name ASC;     
"""
