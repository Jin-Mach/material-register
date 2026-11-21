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
