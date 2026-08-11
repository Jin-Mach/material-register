from PySide6.QtSql import QSqlDatabase, QSqlQuery


class InventoryQueries:
    BASE_QUERY = """
            UPDATE inventory 
            SET stock = stock + ? 
            WHERE commodity_id = ?
    """

    @staticmethod
    def update_inventory_item(db_connection: QSqlDatabase, commodity_id: int, amount: float) -> tuple[bool, str]:
        query = QSqlQuery(db_connection)
        query.prepare(InventoryQueries.BASE_QUERY)
        query.addBindValue(amount)
        query.addBindValue(commodity_id)
        ok = query.exec()
        error = ""
        if not ok:
            error = query.lastError().text()
        return ok, error