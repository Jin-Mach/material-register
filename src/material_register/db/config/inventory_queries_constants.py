INVENTORY_QUERY = """
    SELECT 
        categories.name AS category_name,
        
        commodities.id AS commodity_id,
        commodities.name AS commodity_name,
        commodities.unit AS commodity_unit,

        inventory.stock AS inventory_stock,
        
        commodities.active AS commodity_active 

    FROM inventory inventory
    
    JOIN commodities ON commodities.id = inventory.commodity_id 
    JOIN categories ON commodities.category_id = categories.id

    ORDER BY categories.name ASC, commodities.name ASC;
"""

INVENTORY_HISTORY_DAILY_QUERY = """
    SELECT
        DATE(transactions.created_at, 'localtime') AS transaction_date,

        SUM(
            CASE
                WHEN transactions.type = 'IN'
                    THEN transaction_items.unit_count
                WHEN transactions.type = 'OUT'
                    THEN -transaction_items.unit_count
            END
        ) AS total_movement

    FROM transaction_items

    JOIN transactions
        ON transaction_items.transaction_id = transactions.id

    WHERE transaction_items.commodity_id = ?
        AND transactions.created_at BETWEEN ? AND ?

    GROUP BY DATE(transactions.created_at, 'localtime')
    ORDER BY DATE(transactions.created_at, 'localtime')
"""

INVENTORY_HISTORY_TOTAL_QUERY = """
    SELECT
        COALESCE(
            SUM(
                CASE
                    WHEN transactions.type = 'IN'
                        THEN transaction_items.unit_count
                    WHEN transactions.type = 'OUT'
                        THEN -transaction_items.unit_count
                END
            ),
            0
        ) AS total_movement

    FROM transaction_items

    JOIN transactions
        ON transaction_items.transaction_id = transactions.id

    WHERE transaction_items.commodity_id = ?
        AND transactions.created_at BETWEEN ? AND ?
"""
